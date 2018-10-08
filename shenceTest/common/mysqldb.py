

if __name__=='__main__':
    db=DB()
    db.query("select * from user where mobile=18916409043")
    db.connClose()