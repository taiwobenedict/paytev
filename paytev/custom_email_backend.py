import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        connection_params = self.connection_params()
        self.connection = smtplib.SMTP(**connection_params)
        self.connection.starttls(context=ssl._create_unverified_context())  # Start TLS with custom context
        if self.username and self.password:
            self.connection.login(self.username, self.password)
        return True

    def connection_params(self):
        params = {
            'host': self.host,
            'port': self.port,
        }
        if hasattr(self, 'local_hostname'):
            params['local_hostname'] = self.local_hostname
        if hasattr(self, 'source_address'):
            params['source_address'] = self.source_address
        return params
