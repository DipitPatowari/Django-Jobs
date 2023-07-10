from difflib import context_diff
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Job,ApplyJob
from .forms import CreateJobForm,UpdateJobForm
from users.models import User 
from company.models import Company
from notifications.models import Notif
from resume.models import Resume
from django.core.mail import send_mail
from django.conf import settings


def create_job(request):
    if request.user.is_recruiter and request.user.has_company: 
        if request.method == 'POST':
            form =  CreateJobForm(request.POST)
            if form.is_valid():
                var = form.save(commit=False)
                var.user = request.user
                var.company = request.user.company
                var.save()
                applicants = Resume.objects.filter(title = var.title)
                for applicant in applicants:
                    user = applicant.user
                    #notification
                    Notif.objects.create(
                        user = user,
                        content = f'There is a new job opening for the role of {var.title} offered by {var.company}'
                    )
                    subject = 'There is a new job opening'
                    message = f'There is a new job opening for the role of {var.title} offered by {var.company}'
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    send_mail (subject , message , from_email , recipient_list)

                messages.info(request, 'New job has been created')
                return redirect('dashboard')
            else:
                messages.warning(request, 'Something went wrong')
                return redirect('create-job')
        else:
            form = CreateJobForm()
            context = {'form':form}
            return render(request, 'job/create_job.html', context)
    else:
        messages.warning(request, 'Permission Denied')
        return redirect('dashboard')


def update_job(request, pk):
    job = Job.objects.get(pk=pk)
    if request.method == 'POST':
        form = UpdateJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            applicants = Resume.objects.filter(title = job.title)
            for applicant in applicants:
                user = applicant.user
                #notification
                Notif.objects.create(
                    user = user,
                    content = f'There has been an update in the job offer for the role of {job.title} offered by {job.company}'
                )
                subject = 'There has been an update in the job'
                message = f'There has been an update in the job offer for the role of {job.title} offered by {job.company}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                send_mail (subject , message , from_email , recipient_list)
            messages.info(request, 'Your job info is updated')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Something went wrong')
    else:
        form = UpdateJobForm(instance=job)
        context = {'form':form}
        return render(request, 'job/update_job.html', context)

def _delete_job(pk):
    job = Job.objects.get(pk=pk)
    applicants = Resume.objects.filter(title = job.title)
    for applicant in applicants:
    #notification
        user = applicant.user
        Notif.objects.create(
        user = user,
        content = f'The job is no longer available for the role of {job.title} offered by {job.company}'
        )
        subject = 'There has been an update in the job'
        message = f'The job is no longer available for the role of {job.title} offered by {job.company}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail (subject , message , from_email , recipient_list)
    job.delete()

#delete job
def delete_job(request, pk):
    _delete_job(pk)
    messages.info(request, 'Your job is deleted')
    return redirect('manage-jobs')


def manage_jobs(request):
    jobs = Job.objects.filter(user=request.user, company=request.user.company)
    context = {'jobs':jobs}
    return render(request, 'job/manage_jobs.html', context)

def apply_to_job(request, pk):
    if request.user.is_authenticated and request.user.is_applicant:    #user must be of applicant type to apply
        job = Job.objects.get(pk = pk)

        if ApplyJob.objects.filter(user = request.user, job = pk).exists():  #if user has already applied
            messages.warning(request, 'Permission Denied')
            return redirect('dashboard') 
        else:                           
            ApplyJob.objects.create(                            
                job = job,
                user = request.user,
                status = 'Pending'
            )
            applicant = Resume.objects.get(user=request.user)
            applicant = f'{applicant.first_name} {applicant.surname}'
            #notification
            Notif.objects.create(
                user = job.company.user,
                content = f'{applicant} has applied to your company {job.company} for the role of {job.title}'
            )
            subject = 'You have applied for job'
            message = f'{applicant} has applied to your company {job.company} for the role of {job.title}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [job.user.email]
            send_mail (subject , message , from_email , recipient_list)

            messages.info(request, 'You have successfully applied! Please see dashboard')
            return redirect('dashboard')
    else:
        messages.info(request, 'Please log in to continue')
        return redirect('login')

        
def all_applicants(request, pk):
    job = Job.objects.get(pk=pk)
    # applicants = job.applyjob_set.all()
    applied_jobs = ApplyJob.objects.filter(job = job)
    # for applicant in applied_jobs:
    #     applicant = Resume.objects.get(user = applicant)
    context = {'job':job, 'applied_jobs':applied_jobs}
    return render(request, 'job/all_applicants.html', context)

def applied_jobs(request):
    jobs = ApplyJob.objects.filter(user=request.user)
    context = {'jobs':jobs}
    return render(request, 'job/applied_job.html', context)
    
def _delete_application(applicant_resume, pk):
    application = ApplyJob.objects.get(id = pk)
    Notif.objects.create(
        user = application.job.company.user,
        content = f'{applicant_resume.__str__()} has revoked application from role of {application.job.title} for the company {application.job.company.name}'
    )   
    application.delete()
    
def delete_application(request, job_pk):
    job = Job.objects.get(pk=job_pk)
    application = ApplyJob.objects.get(user = request.user, job = job)
    resume = Resume.objects.get(user = request.user)
    _delete_application(resume, application.id)
    messages.warning(request, 'Your application has been deleted')
    return redirect('dashboard')

def accept_job(request, app_pk):
    application = ApplyJob.objects.get(pk=app_pk)
    application.status = 'Accepted'
    application.save()
    job = application.job
    
    user = application.user
    resume = Resume.objects.get(user = user)
    messages.info(request, f'You have accepted the application for {job.title} from {resume.first_name} {resume.surname}')
    
    # notification to applicant
    Notif.objects.create(
        user = user,
        content = f'CONGRATS! Your application for {job.title} has been accepted.'
    )

    #email to recruiter
    subject = 'Job accepted'
    message = f'You have accepted the application from {resume.first_name} {resume.surname} for the role of {job.title}.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [job.user.email]
    send_mail (subject , message , from_email , recipient_list)

    #email to applicant
    subject = f'Update on {job.title} job application'
    message = f'Dear {resume.first_name} {resume.surname}, we are delighted to inform you that your application to {job.company} for the role of {job.title} has been ACCEPTED. You will be contacted by {job.company} soon. We wish you all the very best.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail (subject , message , from_email , recipient_list)
    
    applied_jobs = ApplyJob.objects.filter(job = job)
    context = {'job':job, 'applied_jobs':applied_jobs}
    return render(request, 'job/all_applicants.html', context)

#delete job
def reject_job(request, app_pk):
    application = ApplyJob.objects.get(pk=app_pk)
    application.status = 'Declined'
    application.save()
    job = application.job
    
    user = application.user
    resume = Resume.objects.get(user = user)
    messages.info(request, f'You have rejected the application for {job.title} from {resume.first_name} {resume.surname}')
    
    # notification to user who applied
    Notif.objects.create(
        user = user,
        content = f'Sorry:( . Your application for {job.title} has been rejected.'
    )

    #email to user who applied
    subject = f'Update on {job.title} job application'
    message = f'Dear {resume.first_name} {resume.surname}, we are very sorry to inform youthat your application to {job.company} for the role of {job.title} has been rejected. We wish you all the very best.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail (subject , message , from_email , recipient_list)

    applied_jobs = ApplyJob.objects.filter(job = job)
    context = {'job':job, 'applied_jobs':applied_jobs}
    return render(request, 'job/all_applicants.html', context)