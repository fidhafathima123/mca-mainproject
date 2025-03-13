from django.contrib import admin
from .models import Child, ChildSkill, TrainerAssignment, Task, TaskSubmission
from trainer.models import Trainer

class ChildSkillInline(admin.TabularInline):
    model = ChildSkill
    extra = 1  # Allows adding one skill by default, more can be added

class TrainerAssignmentInline(admin.TabularInline):
    model = TrainerAssignment
    extra = 1
    autocomplete_fields = ['trainer']

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('user', 'guardian', 'age', 'dob', 'get_email', 'get_subjects', 'get_medical_conditions')
    list_filter = ('age', 'guardian')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'guardian__user__username')
   
    # Display child email in the list
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    # Display subjects in the list
    def get_subjects(self, obj):
        return obj.subjects if obj.subjects else "N/A"
    get_subjects.short_description = 'Subjects'
   
    # Display medical conditions in the list
    def get_medical_conditions(self, obj):
        return obj.medical_conditions if obj.medical_conditions else "N/A"
    get_medical_conditions.short_description = 'Medical Conditions'
    
    # Group the fields in the admin panel
    fieldsets = (
        (None, {
            'fields': ('user', 'guardian')
        }),
        ('Personal Details', {
            'fields': ('age', 'dob', 'subjects', 'medical_conditions')
        }),
    )
   
    # Add inline child skills and trainer assignments in the same page
    inlines = [ChildSkillInline, TrainerAssignmentInline]
   
    # Enable autocomplete for guardian selection
    autocomplete_fields = ['guardian']

@admin.register(ChildSkill)
class ChildSkillAdmin(admin.ModelAdmin):
    list_display = ('child', 'skill_name', 'rating')
    list_filter = ('skill_name', 'rating')
    search_fields = ('child__user__username', 'skill_name')

@admin.register(TrainerAssignment)
class TrainerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('child', 'trainer', 'subject', 'skill', 'assigned_date')
    list_filter = ('subject', 'skill', 'assigned_date')
    search_fields = ('child__user__username', 'trainer__user__username', 'subject', 'skill')
    autocomplete_fields = ['child', 'trainer']