FROM python:3.12.1-slim-bullseye

RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    libpoppler-cpp-dev

# Set MySQL client environment variables
ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mysql"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"
ENV POPPLER_PATH /usr/lib/x86_64-linux-gnu/poppler

# Set environment variables for other packages
ENV GCC_PATH /usr/bin/gcc
ENV GL_LIB_PATH /usr/lib/x86_64-linux-gnu
ENV GL_INCLUDE_PATH /usr/include/GL
ENV GLX_LIB_PATH /usr/lib/x86_64-linux-gnu
ENV GLX_INCLUDE_PATH /usr/include/GL
ENV GLIB_LIB_PATH /usr/lib/x86_64-linux-gnu
ENV GLIB_INCLUDE_PATH /usr/include/glib-2.0
ENV POPPLER_UTILS_PATH /usr/bin

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
