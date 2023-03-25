from django.db import models

class Ebooks(models.Model):
    book_id = models.IntegerField(null=False, auto_created=True, primary_key=True)
    isbn = models.TextField(db_column='ISBN', null=False)  # Field name made lowercase.
    title = models.TextField(null=False)      
    author = models.TextField(null=False)     
    price = models.BigIntegerField(null=False)
    star = models.FloatField(null=False)      
    category = models.TextField(null=False)   
    img = models.TextField(null=False)

    class Meta:
        managed = False
        db_table = 'ebook'


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=13)
    user_name = models.CharField(max_length=10)
    user_pwd = models.CharField(max_length=25)
    birthday = models.DateField()
    join_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'user'

class User_Wanted(models.Model) :
    w_id = models.IntegerField(null=False, auto_created=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Ebooks, on_delete=models.CASCADE)

    class Meta :
        managed = False
        db_table = 'user_wanted'

class User_Read(models.Model) :
    r_id = models.IntegerField(null=False, auto_created=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Ebooks, on_delete=models.CASCADE)

    class Meta :
        managed=False
        db_table = 'user_read'