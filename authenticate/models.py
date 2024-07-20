from django.db import models

# Create your models here.


class Palm(models.Model):
    phnumber = models.CharField(max_length=150)
    username = models.CharField(max_length=150, blank=False, null=False, default="")
    email = models.EmailField(max_length=254, unique= True)
    picture = models.ImageField(upload_to='pics/', null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    def cus_save(self, *args, **kwargs):
        if self.picture and hasattr(self.picture, 'name'):
            self.title = os.path.basename(self.picture.name)
        super(Palm, self).save(*args, **kwargs)


class H5Model(models.Model):
    weights = models.FileField(upload_to='models/weights/')

    def save_weights(self, model):
        filename = "../Veinpattern.h5"
        filepath = os.path.join(os.getcwd(), filename)
        model.save_weights(filepath)
        self.weights.save(filename, files.File(open(filepath, 'rb')))

    def load_weights(self, model):
        filename = "../Veinpattern.h5"
        path = os.path.join(os.getcwd(), "models", "weights")
        print("model path :",path)
        filepath = os.path.join(path, filename)
        with open(filepath, 'wb') as f:
            f.write(self.weights.read())
        model.load_weights(filepath)
        os.remove(filepath)