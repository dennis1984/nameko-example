# -*- coding:utf8 -*-

from nameko.rpc import rpc, RpcProxy
from dynaconf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate

if settings.DEBUG:
    print 'Starting in DEBUG mode'
else:
    print 'Starting in PRODUCTION mode'


def send_email(to, subject, text, files=()):
    """
    发送邮件
    使用影联客的邮箱用户名和密码
    """
    assert isinstance(to, (list, tuple))

    server = {'host': 'smtp.163.com',
              'port': 465,
              'user': 'year2005706',
              'password': 'xxx',
              'prefix': '影联客',
              'postfix': '163.com'}

    _from = '%s@%s' % (server['user'], server['postfix'])

    message = MIMEMultipart()
    message['From'] = '%s<%s>' % (server['prefix'], _from)
    message['Subject'] = subject
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message.attach(MIMEText(text, _subtype='plain', _charset='utf8'))

    try:
        smtp = smtplib.SMTP_SSL(server['host'], server['port'])
        smtp.login(server['user'], server['password'])
        smtp.sendmail(_from, to, message.as_string())
        smtp.close()
    except:
        return False
    return True


class Mail(object):
    name = 'mail'

    @rpc
    def send(self, to, subject, contents):
        send_email(to, subject, contents)


class Compute(object):
    name = 'compute'
    mail = RpcProxy('mail')

    @rpc
    def compute(self, operation, value, other, mail):
        operations = {u'sum': lambda x, y: int(x) + int(y),
                      u'mul': lambda x, y: int(x) * int(y),
                      u'div': lambda x, y: int(x) / int(y),
                      u'sub': lambda x, y: int(x) - int(y)}
        try:
            result = operations[operation](value, other)
        except Exception as e:
            self.mail.send.async(mail, "An error occurred", str(e))
            raise
        else:
            self.mail.send.async(mail,
                                 "Your operation is complete!",
                                 "The result is: %s" % result)
            return result


