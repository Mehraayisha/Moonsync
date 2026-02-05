from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tracker1.models import MenstrualCycle # Import the MenstrualCycle model
from tracker1.ml_utils import predict_cycle_length
from .forms import MenstrualCycleForm
#by sherin

#------
def home(request):
    return render(request, 'home.html') 

def login_redirect(request):
    return redirect('signinup')

def products(request):
    return render(request, 'products.html')
def video(request):
    return render(request, 'video.html')



@login_required
def tracking(request):
    today = datetime.today().date()
    current_hour = datetime.now().hour
    start_of_week = today - timedelta(days=today.weekday())

    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    week_names = [date.strftime("%A")[0] for date in week_dates]

    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    current_day_number = today.day

    cycle_info = None
    period_dates = []
    period_data = None

    user = request.user

    if MenstrualCycle.objects.filter(user=user).exists():
        cycle_info = MenstrualCycle.objects.get(user=user)

        last_period_date = cycle_info.last_period
        period_duration = cycle_info.period_duration

        # Default fallback
        cycle_length = cycle_info.cycle_length

        # Try ML prediction
        try:
            age = cycle_info.age
            bmi = cycle_info.calculate_bmi()

            if age and bmi:
                luteal_length = 14
                total_score = 10
                ovulation_day = 14

                predicted_length = predict_cycle_length(
                    age,
                    bmi,
                    period_duration,
                    luteal_length,
                    total_score,
                    ovulation_day
                )

                cycle_length = predicted_length

        except Exception as e:
            print("ML error:", e)

        print("====================================")
        print("User:", user.username)
        print("Entered cycle length:", cycle_info.cycle_length)
        print("Predicted cycle length:", cycle_length)
        print("Last period:", last_period_date)

        next_period_start, next_period_end = predict_next_period(
            last_period_date,
            cycle_length,
            period_duration
        )

        print("Next period starts:", next_period_start)
        print("Next period ends:", next_period_end)
        print("====================================")

        # CHANGED: Generate ALL period dates for the calendar (entire period duration)
        period_dates = []
        for i in range(period_duration):
            period_day = next_period_start + timedelta(days=i)
            period_dates.append(period_day.strftime('%Y-%m-%d'))

        period_data = get_period_progress(
            last_period_date,
            cycle_length,
            period_duration
        )
        
        # ADDED: Add period_dates to period_data so it's accessible in template
        period_data['period_dates'] = period_dates

    return render(request, "tracking.html", {
        'greeting': greeting,
        'week_names': week_names,
        'week_dates': week_dates,
        'today': today,
        'current_day_number': current_day_number,
        'cycle_info': cycle_info,
        'period_data': period_data,
    })
    
    # REMOVED: Delete the duplicate return statement below

@login_required  # Ensure the user is logged in before accessing this view
def tracker(request):
    # Check if the user has already entered their menstrual cycle details
    user = request.user
    if MenstrualCycle.objects.filter(user=user).exists():
        # If the details are already entered, redirect to the index page
        messages.info(request, "Your cycle details are already saved.")
        return redirect('tracking')  # or you can redirect to any other page like home
    else:
        # If no details are saved, show the details form
        return render(request, 'details.html')


def predict_next_period(last_period, cycle_length, period_duration):
    """
    Predict the next period based on the last period date, cycle length, and period duration.
    
    :param last_period: The date the last period started (datetime object)
    :param cycle_length: The cycle length (in days)
    :param period_duration: The period duration (in days)
    :return: A tuple with the predicted start and end dates of the next period.
    """
    # Ensure last_period is a datetime object
    if isinstance(last_period, str):
        last_period = datetime.strptime(last_period, "%Y-%m-%d")  # Convert string to datetime if needed

    # Predict the start date of the next period (add cycle_length days to the last period)
    next_period_start = last_period + timedelta(days=cycle_length)
    
    # Predict the end date of the next period (add period_duration days to the start date)
    next_period_end = next_period_start + timedelta(days=period_duration)

    return next_period_start, next_period_end



 # Ensure the user is logged in
@login_required
@login_required
def cycle_details(request):
    user = request.user

    try:
        cycle_info = MenstrualCycle.objects.get(user=user)
        return redirect('tracking')
    except MenstrualCycle.DoesNotExist:
        cycle_info = None

    if request.method == 'POST':
        last_period = request.POST.get('last_period')
        cycle_length = request.POST.get('cycle_length')
        period_duration = request.POST.get('period_duration')
        cycle_regular = request.POST.get('cycle_regular') == 'True'

        age = request.POST.get('age')
        height = request.POST.get('height')
        weight = request.POST.get('weight')

        if cycle_info is None:
            cycle_info = MenstrualCycle(user=user)

        cycle_info.last_period = last_period
        cycle_info.cycle_length = cycle_length
        cycle_info.period_duration = period_duration
        cycle_info.cycle_regular = cycle_regular
        cycle_info.age = age
        cycle_info.height = height
        cycle_info.weight = weight

        cycle_info.save()

        messages.success(request, 'Cycle details saved successfully!')
        return redirect('tracking')

    return render(request, 'details.html')

def get_period_progress(last_period_date, cycle_length, period_duration):
    today = datetime.today().date()
    next_period_start, next_period_end = predict_next_period(last_period_date, cycle_length, period_duration)

    if next_period_start <= today <= next_period_end:
        days_into_period = (today - next_period_start).days + 1
        progress = (days_into_period / period_duration) * 100
        
        # Generate period dates for this period
        current_period_dates = [
            (next_period_start + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(period_duration)
        ]
        
        return {
            'on_period': True,
            'progress': round(progress, 2),
            'day_of_period': days_into_period,
            'period_duration': period_duration,
            'days_left': None,
            'period_dates': current_period_dates
        }
    else:
        days_until_next_period = (next_period_start - today).days
        if days_until_next_period < 0:
            days_until_next_period = 0
        
        # Generate future period dates
        future_period_dates = [
            (next_period_start + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(period_duration)
        ]
        
        return {
            'on_period': False,
            'progress': 0,
            'day_of_period': None,
            'period_duration': None,
            'days_left': days_until_next_period,
            'period_dates': future_period_dates
        }