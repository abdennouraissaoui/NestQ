from typing import Dict


def get_report_finished_processing_template(report_name: str) -> Dict[str, str]:
    return {
        "subject": f"NestQ has finished processing the file {report_name}",
        "plainText": f"Great news! NestQ has finished processing the file {report_name}. To view the data, please log in to your NestQ account: https://app.nestq.ai/signin",
        "html": f"""
            <html>
                <body>
                    <p>Great news! NestQ has finished processing the file {report_name}. To view the data, please log in to your NestQ account: <a href="https://app.nestq.ai/signin">app.nestq.ai/signin</a></p>
                </body>
            </html>
            """,
    }


def get_password_reset_template(reset_link: str) -> Dict[str, str]:
    return {
        "subject": "Password Reset Request",
        "plainText": f"""
            You have requested to reset your password.
            Please click on the following link to reset your password: {reset_link}
            This link is only valid for 15 minutes.
            If you did not request this, please ignore this email.
            """,
        "html": f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>You have requested to reset your password.</p>
                    <p>Please click on the following link to reset your password:</p>
                    <a href="{reset_link}">{reset_link}</a>
                    <p>This link is only valid for 15 minutes.</p>
                    <p>If you did not request this, please ignore this email.</p>
                </body>
            </html>
            """,
    }


def get_welcome_template(first_name: str) -> Dict[str, str]:
    return {
        "subject": "Welcome to NestQ",
        "plainText": f"""
            Welcome {first_name} to NestQ!
            Thank you for joining our platform. We're thrilled to have you on board!
            You can sign in to your account anytime by visiting app.nestq.ai/signin.

            If you need any assistance, feel free to reach out.
            """,
        "html": f"""
            <html>
                <body>
                    <h2>Welcome to NestQ!</h2>
                    <p>Hello {first_name},</p>
                    <p>Thank you for joining our platform. We're thrilled to have you on board!</p>
                    <p>You can sign in to your account anytime by visiting <a href="https://app.nestq.ai/signin">app.nestq.ai/signin</a>.</p>
                    <p>If you need any assistance, feel free to reach out.</p>
                </body>
            </html>
            """,
    }


def get_password_changed_template() -> Dict[str, str]:
    return {
        "subject": "Your Password Has Been Changed",
        "plainText": """
            Your NestQ account password has been successfully changed.
            If you did not make this change, please contact us immediately.
            You can sign in to your account using your new password at app.nestq.ai/signin
            """,
        "html": """
            <html>
                <body>
                    <h2>Password Changed Successfully</h2>
                    <p>Your NestQ account password has been successfully changed.</p>
                    <p>If you did not make this change, please contact us immediately.</p>
                    <p>You can sign in to your account using your new password at <a href="https://app.nestq.ai/signin">app.nestq.ai/signin</a></p>
                </body>
            </html>
            """,
    }
