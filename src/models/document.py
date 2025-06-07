"""
نموذج إدارة المستندات لتطبيق الجيل الحديث للأمن والمصاعد
"""
from datetime import datetime
from src.models.db import db
from src.models.user import User

class Document(db.Model):
    """نموذج المستندات"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # بالبايت
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    user = db.relationship('User', backref='documents')
    categories = db.relationship('DocumentCategory', secondary='document_category_links', backref='documents')
    tags = db.relationship('Tag', secondary='document_tag_links', backref='documents')
    
    def __repr__(self):
        return f'<Document {self.title}>'
    
    def to_dict(self):
        """تحويل المستند إلى قاموس"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S') if self.upload_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None,
            'version': self.version,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'is_active': self.is_active,
            'categories': [category.to_dict() for category in self.categories],
            'tags': [tag.to_dict() for tag in self.tags]
        }


class DocumentCategory(db.Model):
    """نموذج تصنيفات المستندات"""
    __tablename__ = 'document_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('document_categories.id'), nullable=True)
    
    # العلاقات
    children = db.relationship('DocumentCategory', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<DocumentCategory {self.name}>'
    
    def to_dict(self):
        """تحويل التصنيف إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id
        }


class DocumentCategoryLink(db.Model):
    """نموذج ربط المستندات بالتصنيفات"""
    __tablename__ = 'document_category_links'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('document_categories.id'), nullable=False)
    
    def __repr__(self):
        return f'<DocumentCategoryLink {self.document_id}-{self.category_id}>'


class Tag(db.Model):
    """نموذج الوسوم"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """تحويل الوسم إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name
        }


class DocumentTagLink(db.Model):
    """نموذج ربط المستندات بالوسوم"""
    __tablename__ = 'document_tag_links'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    
    def __repr__(self):
        return f'<DocumentTagLink {self.document_id}-{self.tag_id}>'


class DocumentPermission(db.Model):
    """نموذج صلاحيات المستندات"""
    __tablename__ = 'document_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_type = db.Column(db.String(20), nullable=False)  # read, write, delete
    
    # العلاقات
    document = db.relationship('Document', backref='permissions')
    user = db.relationship('User', backref='document_permissions')
    
    def __repr__(self):
        return f'<DocumentPermission {self.document_id}-{self.user_id}-{self.permission_type}>'


class DocumentEntityLink(db.Model):
    """نموذج ربط المستندات بالكيانات الأخرى"""
    __tablename__ = 'document_entity_links'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # contract, client, project, elevator
    entity_id = db.Column(db.Integer, nullable=False)
    
    # العلاقات
    document = db.relationship('Document', backref='entity_links')
    
    def __repr__(self):
        return f'<DocumentEntityLink {self.document_id}-{self.entity_type}-{self.entity_id}>'


class DocumentVersion(db.Model):
    """نموذج إصدارات المستندات"""
    __tablename__ = 'document_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # العلاقات
    document = db.relationship('Document', backref='versions')
    user = db.relationship('User', backref='document_versions')
    
    def __repr__(self):
        return f'<DocumentVersion {self.document_id}-{self.version_number}>'
