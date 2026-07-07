@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return AuthService().login(db, data)