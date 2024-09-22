FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . /code/

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py seed_data

# Command to run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

