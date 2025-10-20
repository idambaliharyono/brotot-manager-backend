from curses.ascii import HT
from datetime import date
from operator import imod
from urllib import response
import cloudinary
from PIL import Image
import tempfile
import cloudinary.uploader
import cloudinary.uploader
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
supabaseUrl= os.getenv('SUPABASE_URL')
supabaseKey = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabaseUrl, supabaseKey)

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_SECRET")
)
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: LoginRequest):
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    print("request_username:", request.username)
    print('request password:', request.password)
    print('username should be:', username)
    print('password should be:', password)
    if str(request.username) != str(username) or str(request.password) != str(password):
        raise HTTPException(status_code=401, detail="invalid username or password")

    return {"message": "Login Successful", "user": username}
    
@app.get("/ping")
def ping():
    return{"status": "ok"}


@app.post("/registration")
def registration(
    nickname :str = Form(...),
    full_name :str = Form(...),
    gender :str = Form(...),
    birthdate :date = Form(...),
    phone_number :str = Form(...),
    medical_info :str = Form(...),
    fitness_goal :str = Form(...),
    prefered_workout_time :str = Form(...),
    photo : UploadFile = File(...)
):


    def UploadCloudinary(photo):
        temp_file_path = None
        image = Image.open(photo.file)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                image.save(temp_file, format="JPEG")
                temp_file_path = temp_file.name

                upload_result = cloudinary.uploader.upload(temp_file_path, folder="gym_members")
                if "url" in upload_result:
                    return str(upload_result.get('url'))
                else:
                    return None
        except Exception as e:
            return None
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    photo_url = UploadCloudinary(photo)
    if not photo_url: 
        raise HTTPException(status_code=500, detail="Photo upload failed")
    
    phone_number_int = int(phone_number)

    response = (
        supabase.table("Members")
        .insert({
            "nick_name": nickname,
            "full_name": full_name,
            "gender": gender,
            "birth_date": birthdate.isoformat(),
            "phone_number": phone_number_int,
            "medical_info": medical_info,
            "fitness_goal": fitness_goal,
            "prefered_workout_time": prefered_workout_time,
            "photo_url": photo_url
            
        })
        .execute()
    )
    return {"message": "New Member Registered Successfully!", "response": response}
