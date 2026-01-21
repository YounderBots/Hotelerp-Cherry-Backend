from sqlalchemy import Boolean, Column,String, DateTime, LargeBinary ,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time,Date,DateTime,BLOB, JSON,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models import engine
import bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
   
#-----------------------Room Reservation
#Room Reservation, Group Reservation, Check in Check out
class Room_Reservation(Base):
    __tablename__ = "room_reservation"

    id = Column(Integer, primary_key=True, index=True)
    Room_Reservation_ID = Column(String(255), unique=True, index=True)
    Salutation = Column(String(100), nullable=True, index=True)
    First_Name = Column(String(100), nullable=True, index=True)
    Last_Name = Column(String(100), nullable=True, index=True)
    Phone_Number = Column(String(20), nullable=False, index=True)
    Email = Column(String(100), nullable=True, index=True)
    Arrival_Date = Column(Date, nullable=False, index=True)
    Departure_Date = Column(Date, nullable=False, index=True)
    No_of_nights = Column(Integer, nullable=False, index=True)
    Room_Type = Column(JSON, nullable=True)
    Rate_Type = Column(JSON, nullable=True, index=True)  # NEW FIELD
    Room_No = Column(JSON, nullable=True)
    No_of_rooms = Column(Integer, nullable=True, index=True)
    No_Of_Adults = Column(String(100), nullable=True, index=True)
    No_Of_Childs = Column(String(100), nullable=True, index=True)
    Payment_mode = Column(String(255), nullable=True, index=True)
    Extra_Bed_Count = Column(Integer, nullable=True, index=True)
    Extra_Bed_cost = Column(Float, nullable=True, index=True)
    Total_Amount = Column(Float, nullable=True, index=True)
    Tax_Percentage = Column(Float, nullable=True, index=True)
    Tax_Amount = Column(Float, nullable=True, index=True)
    Discount_Percentage = Column(Float, nullable=True, index=True)
    Discount_Amount = Column(Float, nullable=True, index=True)
    extra_charges = Column(Float, nullable=True, index=True)
    Overall_Amount = Column(Float, nullable=True, index=True)
    Paid_Amount = Column(Float, nullable=True, index=True)
    Balance_Amount = Column(Float, nullable=True, index=True)
    Extra_Amount = Column(Float, nullable=True, index=True)
    Booking_Status = Column(String(100), nullable=True, index=True)
    Reservation_Type = Column(String(50), nullable=False, index=True)
    Room_Complementry = Column(String(100), nullable=True, index=True)
    Common_Complementry = Column(String(100), nullable=True, index=True)
    Identity_type = Column(String(100), nullable=True, index=True)
    Proof_Document = Column(String(100), nullable=True, index=True)
    Confirmation_code = Column(String(100), nullable=True, index=True)

    token = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)


#Particular Room Details -  Reservation, Group Reservation, Check in Check out
class Room_Details(Base): 
    __tablename__ = "room_details"
    id = Column(Integer, primary_key=True, index=True)
    Reservation_Id = Column(String(255), index=True)
    Room_category = Column(String(255), nullable=False)  
    Available_rooms = Column(String(255), nullable=False) 
    Total_Adults = Column(String(255), nullable=False) 
    Total_Child = Column(String(255), nullable=False) 
    Arrival_Date = Column(Date, nullable=False, index=True)
    Departure_Date = Column(Date, nullable=False, index=True)
    Booking_Status = Column(String(100), nullable=True, index=True)
    Reservation_Type = Column(String(50), nullable=False, index=True)  # "Reservation", "Group_Reservation", or "Checkin"
    Extra_Bed_Count = Column(Integer, nullable=True, index=True) 
    Extra_Bed_cost = Column(Float, nullable=True, index=True) 
    total_Amount = Column(Float, nullable=True, index=True) 
    Room_Complementry = Column(String(100), nullable=True, index=True) # Yes or No 
    
    token = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#Reservation Amount Paid History
class Reser_AmountPaidHistory(Base): 
    __tablename__ = "reservation_amountpaidhistory"
    id = Column(Integer, primary_key=True, index=True)
    Reservation_Id = Column(String(255), index=True)
    user_id = Column(String(255), nullable=False,index=True)
    Amount = Column(Float, nullable=False, index=True) 
    paid_date = Column(Date, nullable=False,index=True)
    payment_method = Column(String(255), nullable=False,index=True)
    
    token = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)
 
#Customr Room Reserved Complementry History   
class Room_Complementry_History(Base): 
    __tablename__ = "room_complementry_history"
    id = Column(Integer, primary_key=True, index=True)
    Reservation_Id = Column(String(255), index=True)
    Room_Complementry_Id = Column(String(255), nullable=False)  
    Complementry_Name = Column(String(255), nullable=False) 
    Description = Column(String(255), nullable=False) 
    
    token = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#Customr Reserved Common Complementry History
class Common_Complementry_History(Base): 
    __tablename__ = "common_complementry_history"
    id = Column(Integer, primary_key=True, index=True)
    Reservation_id = Column(String(255), index=True)
    Common_Complementry_Id = Column(String(255), nullable=False)  
    Complementry_Name = Column(String(255), nullable=False) 
    Description = Column(String(255), nullable=False) 
    
    token = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)


#Room Booking
class Room_Booking(Base):
    
    __tablename__ = "room_booking"

    id = Column(Integer, primary_key=True, index=True)
    Room_Booking_Id = Column(String(255), unique=True, index=True)  
    Salutation = Column(String(100), nullable=True, index=True)
    First_Name = Column(String(100), nullable=True, index=True)
    Last_Name = Column(String(100), nullable=True, index=True)
    Phone_Number = Column(String(20), nullable=False, index=True)
    Email = Column(String(100), nullable=True, index=True)
    Arrival_Date = Column(Date, nullable=False, index=True)
    Departure_Date = Column(Date, nullable=False, index=True)
    No_of_nights = Column(Integer, nullable=False, index=True)
    Room_Type = Column(JSON, nullable=True)  
    No_of_rooms = Column(Integer, nullable=True, index=True)  
    No_Of_Adults = Column(String(100), nullable=True, index=True)
    No_Of_Childs = Column(String(100), nullable=True, index=True)
    
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#------------------> House Keeping

#Housekeeper Task
class Housekeeper_Task(Base):
    __tablename__ = "housekeeper_task"

    id = Column(Integer, primary_key=True, index=True)
    Employee_ID = Column(String(255), nullable=True, index=True) 
    First_Name = Column(String(100), nullable=True, index=True)
    Sur_Name = Column(String(100), nullable=True, index=True)
    Sch_Date = Column(Date, nullable=True, index=True)
    Sch_Time = Column(Time, nullable=True, index=True)
    Room_No = Column(Integer, nullable=True, index=True)
    Task_Type = Column(String(100), nullable=True, index=True)
    Assign_Staff = Column(String(100), nullable=True, index=True)
    Task_Status = Column(String(100), nullable=True, index=True)
    Room_Status = Column(String(100), nullable=True, index=True)
    Lost_Found = Column(String(255), nullable=True, index=True)
    Special_Instructions = Column(String(100), nullable=False, index=True)
    
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#Housekeeper Incident
class HSK_Room_Incident(Base):

    __tablename__ = "hsk_room_incident"
    id = Column(Integer, primary_key=True, index=True)
    Room_No = Column(Integer, nullable=True, index=True)
    Date_of_Incident = Column(Date, nullable=True, index=True)
    Time_of_Incident = Column(Time, nullable=True, index=True)
    Incident_Desc = Column(String(100), nullable=True, index=True)
    HSK_Involved_Staff = Column(String(100), nullable=True, index=True)
    Severity = Column(String(100), nullable=True, index=True)
    Witnesses = Column(String(100), nullable=True, index=True)
    Actions_Taken = Column(String(100), nullable=True, index=True)
    Reported_By = Column(String(100), nullable=True, index=True)
    Date_of_Report = Column(String(100), nullable=True, index=True)
    File = Column(String(100), nullable=True, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#------------------------->Laundary Management

#Laundry Items
class Laundry_Items(Base):
    __tablename__ = "laundry_items"
    id = Column(Integer, primary_key=True, index=True)
    Items =Column(String(100), nullable=False, index=True)
    Price =Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#Laundry Management
class Laundry_Management(Base):
    __tablename__ ="laundry_management"
    id = Column(Integer, primary_key=True, index=True)
    Rooms_ID = Column(String(100), nullable=True, index=True)
    Name= Column(String(100), nullable=True, index=True)
    Mobile = Column(String(100), nullable=False, index=True)
    Date_of_Laundry =Column(String(100), nullable=False, index=True)
    Items = Column(JSON)
    Count_of_items = Column(JSON)
    Price = Column(JSON)
    Total_items =Column(Integer, nullable=False, index=True)
    Net_price =Column(Integer, nullable=False, index=True)
    Laundry_status =Column(String(100), nullable=False, index=True)
    Special_Instructions = Column(String(100), nullable=False, index=True)


    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)


#----------------------------------------->Customer Data
# Customer table
class Customer_Data(Base):
    __tablename__ = "customer_data"

    id = Column(Integer, primary_key=True, index=True)
    Customer_ID = Column(String(100), nullable=True, index=True)
    Photo = Column(String(100), nullable=True, index=True)
    First_Name = Column(String(100), nullable=False, index=True)
    Last_Name = Column(String(100), nullable=False, index=True)
    Email = Column(String(100), nullable=False, index=True)
    Mobile = Column(String(100), nullable=False, index=True)
    D_O_B = Column(String(100), nullable=False, index=True)
    Address = Column(String(100), nullable=False, index=True)
    City = Column(String(100), nullable=False, index=True)
    Gender = Column(String(100), nullable=False, index=True)
    State = Column(String(100), nullable=False, index=True)
    Postal_code = Column(String(100), nullable=False, index=True)
    Country = Column(String(100), nullable=False, index=True)
    Marital_status = Column(String(100), nullable=False, index=True)
    VIP_status = Column(String(100), nullable=False, index=True)
    Number_Of_Guests = Column(String(100), nullable=False, index=True)
    Number_Of_Adults = Column(String(100), nullable=False, index=True)
    Names_Of_Adults = Column(JSON, nullable=False, index=True)
    Number_Of_Childs = Column(String(100), nullable=False, index=True)
    Names_Of_Childs = Column(JSON, nullable=False, index=True)
    Identification_Type_id = Column(String(100), nullable=False, index=True)
    Identification_Proof = Column(String(100), nullable=False, index=True)
    Reservation_ID = Column(String(100), nullable=True, index=True)
    Check_in_Date = Column(String(100), nullable=True, index=True)
    Check_in_Time = Column(String(100), nullable=True, index=True)
    Check_Out_Date = Column(String(100), nullable=True, index=True)
    Check_Out_Time = Column(String(100), nullable=True, index=True)
    Rooms_ID = Column(JSON, nullable=True, index=True)
    Room_Type_Id = Column(JSON, nullable=True, index=True)
    Bed_Type_Id = Column(JSON, nullable=True, index=True)
    Credit_card_Info = Column(String(100), nullable=True, index=True)
    Debit_card_Info = Column(String(100), nullable=True, index=True)
    Purpose_Of_Visit = Column(String(100), nullable=True, index=True)
    Emergency_Name = Column(String(100), nullable=True, index=True)
    Emergency_Contact = Column(String(100), nullable=True, index=True)
    Emergency_Relationship = Column(String(100), nullable=True, index=True)
    Consent_for_Data_Use = Column(String(100), nullable=True, index=True)
    Acknowledgment_of_Hotel_Policies = Column(String(100), nullable=True, index=True)
    Special_services_info = Column(JSON, nullable=True, index=True)
    Total_amount = Column(String(100), nullable=True, index=True)
    Tax_amount = Column(String(100), nullable=True, index=True)
    Discount_amount = Column(String(100), nullable=True, index=True)
    Laundry_amount = Column(String(100), nullable=True, index=True)
    Bar_amount = Column(String(100), nullable=True, index=True)
    Cafe_amount = Column(String(100), nullable=True, index=True)
    Resturant_amount = Column(String(100), nullable=True, index=True)
    Special_services_amount = Column(String(100), nullable=True, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#------------------------------->HRM
# Employee table
class Employee_Data(Base):
    __tablename__ = "employee_data"

    id = Column(Integer, primary_key=True, index=True)
    Employee_ID = Column(String(100), nullable=False, index=True)
    Photo = Column(String(100), nullable=False, index=True)
    First_Name = Column(String(100), nullable=False, index=True)
    Last_Name = Column(String(100), nullable=False, index=True)
    Personal_Email = Column(String(100), nullable=False, index=True)
    Company_Email = Column(String(100), nullable=False, index=True)
    Password = Column(String(100), nullable=False, index=True)
    Mobile = Column(String(100), nullable=False, index=True)
    Alternative_Mobile = Column(String(100), nullable=False, index=True)
    D_O_B = Column(String(100), nullable=False, index=True)
    Gender = Column(String(100), nullable=False, index=True)
    Address = Column(String(100), nullable=False, index=True)
    City = Column(String(100), nullable=False, index=True)
    State = Column(String(100), nullable=False, index=True)
    Postal_code = Column(String(100), nullable=False, index=True)
    Country = Column(String(100), nullable=False, index=True)
    Role_id = Column(String(100), nullable=False, index=True)
    Department_id = Column(String(100), nullable=False, index=True)
    Date_Of_Joining = Column(String(100), nullable=False, index=True)
    Salary_details = Column(String(100), nullable=False, index=True)
    Experience = Column(String(100), nullable=False, index=True)
    Register_Code = Column(String(100), nullable=False, index=True)
    Marital_Status = Column(String(100), nullable=False, index=True)
    Notes = Column(String(100), nullable=False, index=True)
    Emergency_Name = Column(String(100), nullable=False, index=True)
    Emergency_Contact = Column(String(100), nullable=False, index=True)
    Emergency_Relationship = Column(String(100), nullable=False, index=True)
    Acknowledgment_of_Hotel_Policies = Column(String(100), nullable=True, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)
 
#----------------------------->Master Data
# Employee Role
class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), nullable=False, index=True)
    
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)    

#Language
class Language(Base):
    __tablename__ = "language"

    id = Column(Integer, primary_key=True, index=True)
    Language_Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#Quantity
class Quantity(Base):
    __tablename__ = "quantity"

    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), nullable=False, index=True)

    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True) 

#Role Permission
class Role_Permission(Base): 
    __tablename__ = "role_permission"
    
    id = Column(Integer, primary_key=True, index=True)
    Role_ID = Column(String(255), unique=True, index=True) 
    Modules_Data = Column(JSON) 
    
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

#-----------------------------------> Inquiry Table
class Inquiry(Base):
    __tablename__ = "inquiry"

    id = Column(Integer, primary_key=True, index=True)
    inquiry_mode = Column(String(255), nullable=False, index=True) # ---- > Online, Offline
    guest_name = Column(String(255), nullable=False, index=True)
    response = Column(String(255), nullable=False, index=True)
    followup = Column(String(255), nullable=False, index=True)
    incidents = Column(String(255), nullable=False)
    inquiry_status = Column(String(100), nullable=False, index=True) # ---- > In progress, Completed
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True) 

#Theme color  
class Themes(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    primary_color= Column(String(100), nullable=False, index=True)
    button_color = Column(String(100), nullable=False, index=True)
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, onupdate=datetime.utcnow())
    company_id = Column(String(100), nullable=False, index=True) 
    
Base.metadata.create_all(bind=engine)
