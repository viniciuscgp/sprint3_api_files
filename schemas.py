from app import ma


class FilesSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'file_name', 'file_content', 'tags')


class FilesListSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'file_name')
