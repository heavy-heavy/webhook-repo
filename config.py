import os

class Config:
    MONGO_URI=os.getenv('MONGO_URI','your_uri')
    PORT=int(os.getenv('PORT',5000))
    DEBUG=os.getenv('DEBUG','TRUE')=='True'
    SECRET=os.getenv('WEBHOOK_SECRET','your_key')


    
