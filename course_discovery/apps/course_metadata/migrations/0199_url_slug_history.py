# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-01 00:43
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_add_case_record_type_id'),
        ('course_metadata', '0198_add_course_type_and_friends'),
    ]

    def migrate_data_forward(apps, schema_editor):
        published_drafts = []
        Course = apps.get_model('course_metadata', 'course')
        CourseUrlSlug = apps.get_model('course_metadata', 'courseUrlSlug')
        for instance in Course.everything.all().order_by('draft'):

            if instance.pk not in published_drafts:
                historical_slug = CourseUrlSlug.objects.create(
                    course=instance,
                    partner=instance.partner,
                    is_active=True,
                    is_active_on_draft=True
                )
                historical_slug.save()

                if instance.draft_version:
                    published_drafts.append(instance.draft_version_id)

    def migrate_data_backwards(apps, schema_editor):
        Course = apps.get_model('course_metadata', 'course')
        CourseUrlSlugHistory = apps.get_model('course_metadata', 'courseUrlSlug')

        def getActiveSlug(course_instance):
            try:
                active_slug = CourseUrlSlugHistory.objects.get(course=course_instance, is_active=True)
                return active_slug.url_slug
            except ObjectDoesNotExist:
                pass

            try:
                official_version = Course.everything.get(draft_version_id=course_instance.id)
                active_slug = CourseUrlSlugHistory.objects.get(course=official_version,is_active_on_draft=True)
                return active_slug.url_slug
            except ObjectDoesNotExist:
                    pass
            return ''

        for instance in Course.everything.all():
            instance.url_slug = getActiveSlug(instance)
            instance.save()


    operations = [
        migrations.CreateModel(
            name='CourseUrlSlug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url_slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from='course__title')),
                ('is_active', models.BooleanField(default=False)),
                ('is_active_on_draft', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set([('partner', 'uuid', 'draft'), ('partner', 'key', 'draft')]),
        ),
        migrations.AddField(
            model_name='courseurlslug',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='url_slug_history', to='course_metadata.Course'),
        ),
        migrations.AddField(
            model_name='courseurlslug',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Partner'),
        ),
        migrations.AlterUniqueTogether(
            name='courseurlslug',
            unique_together=set([('partner', 'url_slug')]),
        ),
        migrations.RunPython(
            migrate_data_forward,
            migrate_data_backwards
        )
    ]
