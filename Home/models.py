from distutils.command.upload import upload
from tkinter.tix import Tree
from django.db import models
from django.contrib.auth.models import User

# Create your models here.    
class CustomerProfile(models.Model):
    gender = (
        ('Male', 'male'),
        ('Female', 'female'),
        ('Other', 'other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    firstname = models.CharField(max_length=100, blank=True, default='')
    lastname = models.CharField(max_length=100, blank=True, default='')
    phonenumber = models.CharField(max_length=100,  blank=True, default='')
    profile_img = models.ImageField(upload_to= 'profile_img', blank=True, null= True)
    gender = models.CharField(max_length=10, choices=gender, blank=True, null=True)
    country = models.CharField(max_length=128,blank=True, default='')
    state = models.CharField(max_length=128,blank=True, default='')
    city = models.CharField(max_length=128, blank=True, default='')
    street = models.CharField( max_length=128, blank=True, default='')
    zip_code = models.CharField(max_length=10, blank=True, default='')
    nationa_id = models.FileField(upload_to='user_doc', blank=True, null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

class Bookings(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        
    )
    customer = models.ForeignKey(CustomerProfile, null=True, on_delete= models.SET_NULL)
    hotelname = models.CharField(max_length=100, null= True, blank=True)
    hotel_img = models.ImageField(upload_to= 'hotels',null=True,blank= True)
    location = models.CharField(max_length=100, null= True)
    room_des = models.CharField(max_length=200, null= True)
    start_date = models.DateField(null=True,blank= True)
    end_date = models.DateField(null=True,blank= True)
    total_amount = models.IntegerField(null=True,blank= True)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.customer.user.username
    
class Contact(models.Model):
    customer = models.ForeignKey(CustomerProfile, null=True, on_delete= models.SET_NULL)
    name = models.CharField(max_length=128, default='', blank=True)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length= 250, default='')
    message = models.CharField(max_length= 1000, default='')