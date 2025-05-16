import flask
from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from app.models import Upload, User, Share
from app import db
from flask import Blueprint, session, redirect, url_for, render_template
from .utils import require_csrf_token, require_login

# Blueprint setup
share_bp = flask.Blueprint(
    "share",
    __name__,
    url_prefix="/share",
)

@share_bp.route('/')
@require_login
def home():
    user_id = session['user_id']

    # Get user's uploaded analyses
    uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.timestamp.desc()).all()
    
    return render_template('share.html', uploads=uploads)

@share_bp.route('/test')
def test():
    return "Share blueprint test route is working!"


@share_bp.route('/send_email', methods=['POST'])
def send_email():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to share analysis'}), 401
    
    user_id = session['user_id']
    
    current_user = User.query.filter_by(id=user_id).first()
    if not current_user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Get form data
    data = request.json
    upload_id = data.get('uploadId')
    emails = data.get('emails', '').split(',')
    message_text = data.get('message', '')
    
    # Validation
    if not upload_id or not emails:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Clean and validate email addresses
    valid_emails = []
    invalid_emails = []
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    for email in emails:
        email = email.strip()
        if re.match(email_regex, email):
            valid_emails.append(email)
        elif email:  # Only add non-empty invalid emails
            invalid_emails.append(email)
    
    if not valid_emails:
        return jsonify({'success': False, 'message': 'No valid email addresses provided'}), 400
    
    # Get uploaded analysis
    upload = Upload.query.get(upload_id)
    if not upload:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404
    
    if str(upload.user_id) != str(user_id):
        return jsonify({'success': False, 'message': 'You do not have permission to share this analysis'}), 403
    
    # Use temporary file for PDF output
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        pdf_path = temp_file.name
    
    try:
        server_url = request.host_url.rstrip('/')
        url = f"{server_url}/analyze/result/{upload_id}?export_pdf=true"
        subprocess.run(['wkhtmltopdf', url, pdf_path], check=True)
        
        # Iterate through all valid email addresses
        for email in valid_emails:
            # Check if recipient is a system user - using filter_by
            recipient = User.query.filter_by(email=email).first()
            
            # Create Share record
            share = Share(
                upload_id=upload_id,
                sender_id=user_id,
                recipient_id=recipient.id if recipient else None,
                recipient_email=email if not recipient else None,
                message=message_text,
                timestamp=datetime.utcnow()
            )
            db.session.add(share)
            
            # Create email object
            msg = Message(
                subject=f"SentiSocial Analysis: {upload.title}",
                recipients=[email]
            )
            
            # Set email content
            msg.body = f"""
Hello,

{current_user.first_name} {current_user.last_name} has shared a sentiment analysis with you from SentiSocial.

Analysis: {upload.title}
Platform: {upload.platform}
{f"Message: {message_text}" if message_text else ""}

The analysis report is attached to this email.

Best regards,
SentiSocial Team
            """
            
            # Add PDF attachment
            with open(pdf_path, 'rb') as pdf:
                msg.attach(
                    filename=f"{upload.title.replace(' ', '_')}_analysis.pdf",
                    content_type='application/pdf',
                    data=pdf.read()
                )
            
            # Send email
            mail.send(msg)
        
        # Commit database changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Analysis shared with {len(valid_emails)} recipients',
            'invalidEmails': invalid_emails if invalid_emails else None
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sharing analysis: {str(e)}")
        return jsonify({'success': False, 'message': f'Error sharing analysis: {str(e)}'}), 500
    
    finally:
        # Delete temporary PDF file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

@share_bp.route('/check_session')
def check_session():
    """Check current session status"""
    result = {
        'session_exists': bool(session),
        'user_id_in_session': 'user_id' in session,
        'user_id': session.get('user_id') if 'user_id' in session else None,
    }
    
    # If user_id exists in session, try to get the user
    if 'user_id' in session:
        user_id = session.get('user_id')
        try:
            user = User.query.get(user_id)
            result['user_found'] = bool(user)
            if user:
                result['user_info'] = {
                    'id': user.id,
                    'email': user.email
                }
            else:
                result['user_found'] = False
                
                # List all users
                all_users = User.query.all()
                result['all_users'] = [{'id': u.id, 'email': u.email} for u in all_users]
        except Exception as e:
            result['error'] = str(e)
    
    return jsonify(result)