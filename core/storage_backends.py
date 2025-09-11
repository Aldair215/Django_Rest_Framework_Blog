from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    custom_domain = settings.AWS_S3_DOMAIN
    
class PublicMediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION #Define la ubicación de los archivos multimedia
    default_acl = 'public-read' #Define el control de acceso predeterminado para los archivos multimedia
    file_overwrite = False #Evita que los archivos con el mismo nombre se sobrescriban