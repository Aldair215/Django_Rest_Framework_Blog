from rest_framework import serializers

from .models import Post, Category, Heading, PostView



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class HeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heading
        fields = (
            'title',
            'slug',
            'level',
            'order',
        )

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )

class PostViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostView
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    headings = HeadingSerializer(many=True,read_only=True)
    view_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_view_count(self, obj):
        return obj.post_view.count()


class PostListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    view_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 
                  'title', 
                  'description', 
                  'thumbnail', 
                  'slug', 
                  'category', 
                  'view_count',
                  )
    def get_view_count(self, obj):
        return obj.post_view.count()
       



