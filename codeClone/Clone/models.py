from django.db import models

class PythonFile(models.Model):
    file1 = models.FileField(upload_to='python_files/')
    file2 = models.FileField(upload_to='python_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
