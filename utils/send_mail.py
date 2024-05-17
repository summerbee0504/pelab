import smtplib
from email.mime.text import MIMEText
import os

def send_gmail(mail_body):
    email = os.getenv('GOOGLE_ACCOUNT')
    app_passwd = os.getenv('GOOGLE_APPLICATION_PASSWORD')
    mail_to = os.getenv('MAIL_TO')

    """ メッセージのオブジェクト """
    msg = MIMEText(mail_body, "plain", "utf-8")
    msg['Subject'] = "【PELAB】エラーメッセージ"
    msg['From'] = email
    msg['To'] = mail_to

    # エラーキャッチ
    try:
        """ SMTPメールサーバーに接続 """
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)  # SMTPオブジェクトを作成。smtp.gmail.comのSMTPサーバーの587番ポートを設定。
        smtpobj.ehlo()                                 # SMTPサーバとの接続を確立
        smtpobj.starttls()                             # TLS暗号化通信開始
        app_passwd = app_passwd      # アプリパスワード
        smtpobj.login(email, app_passwd)          # SMTPサーバーへログイン

        """ メール送信 """
        smtpobj.sendmail(email, mail_to, msg.as_string())

        """ SMTPサーバーとの接続解除 """
        smtpobj.quit()

    except Exception as e:
        raise Exception("Error: Failed to send email; %s" % e)
    
    return "Success"