import os

class Config:
    MONGO_URI=os.getenv('MONGO_URI','mongodb+srv://singhprabhav09:sqYtpSnDdPMVEIXG@cluster0.vgmm5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    PORT=int(os.getenv('PORT',5000))
    DEBUG=os.getenv('DEBUG','TRUE')=='True'
    SECRET=os.getenv('WEBHOOK_SECRET','heiurnh73vi4btvri3yn4r')


    