from abc import ABC, abstractmethod 
class EmailService(ABC): 
    @abstractmethod 
    def send_email( 
            self, to_email: str, 
            subject: str, 
            body: str,
            html: bool = False 
        ): 
        pass