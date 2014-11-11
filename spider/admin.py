from mongoadmin import site, DocumentAdmin

from app.models import AppDocument

# Register your models here.

class AppDocumentAdmin(DocumentAdmin):
	pass
site.register(AppDocument, AppDocumentAdmin)
