FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Sets language to UTF8 : this works in pretty much all cases
ENV LANG en_US.UTF-8
RUN locale-gen $LANG

ENV DOCKER_ANDROID_LANG en_US
ENV DOCKER_ANDROID_DISPLAY_NAME mobileci-docker

# Never ask for confirmations
ENV DEBIAN_FRONTEND noninteractive

# Update apt-get
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -yq \
      libc6:i386 \
      build-essential \
      libssl-dev \
      ruby \
      ruby-dev \
      unzip \
      locales \
      --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN gem install bundler

# Install apt-add-repository
RUN apt-get update && \
    apt-get -y install software-properties-common python-software-properties && \
    rm -rf /var/lib/apt/lists/*

# Install Java
RUN apt-add-repository ppa:openjdk-r/ppa && \
    apt-get update && \
    apt-get -y install openjdk-8-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Export JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

RUN apt-get update && \
    apt-get -y install curl && \
    rm -rf /var/lib/apt/lists/*

# Download and untar Android SDK tools
RUN mkdir -p /opt/android-sdk && \
    curl -sLo tools.zip https://dl.google.com/android/repository/tools_r25.2.5-linux.zip && \
    unzip -q tools.zip -d /opt/android-sdk && \
    rm tools.zip

# Set environment variable
ENV ANDROID_HOME /opt/android-sdk
ENV PATH ${ANDROID_HOME}/tools:$ANDROID_HOME/platform-tools:$PATH

RUN mkdir -p $ANDROID_HOME/licenses && \
    echo -e "8933bad161af4178b1185d1a37fbf41ea5269c55" > $ANDROID_HOME/licenses/android-sdk-license && \
    echo -e "d56f5187479451eabf01fb78af6dfcb131a6481e" >> $ANDROID_HOME/licenses/android-sdk-license && \
    echo -e "84831b9409646a918e30573bab4c9c91346d8abd" >> $ANDROID_HOME/licenses/android-sdk-preview-license && \
    echo -e "d975f751698a77b662f1254ddbeed3901e976f5a" >> $ANDROID_HOME/licenses/intel-android-extra-license

# Update and install using sdkmanager 
RUN $ANDROID_HOME/tools/bin/sdkmanager "tools" "platform-tools"
#RUN $ANDROID_HOME/tools/bin/sdkmanager "build-tools;26.0.2" "build-tools;25.0.3"
RUN $ANDROID_HOME/tools/bin/sdkmanager "build-tools;21.1.2"
#RUN $ANDROID_HOME/tools/bin/sdkmanager "platforms;android-26" "platforms;android-25" "platforms;android-24" "platforms;android-23"
RUN $ANDROID_HOME/tools/bin/sdkmanager "platforms;android-21"
#RUN $ANDROID_HOME/tools/bin/sdkmanager "extras;android;m2repository" "extras;google;m2repository"
#RUN $ANDROID_HOME/tools/bin/sdkmanager "extras;m2repository;com;android;support;constraint;constraint-layout;1.0.2"
#RUN $ANDROID_HOME/tools/bin/sdkmanager "extras;m2repository;com;android;support;constraint;constraint-layout-solver;1.0.2"
ENV LD_LIBRARY_PATH ${ANDROID_HOME}/emulator/lib64:${ANDROID_HOME}/emulator/lib64/qt/lib

# Install Android NDK
#ENV ANDROID_NDK_VERSION r15c
#RUN FILE=android-ndk-${ANDROID_NDK_VERSION}-linux-x86_64.zip && \
#    curl -sLo $FILE http://dl.google.com/android/repository/$FILE && \
#    unzip -q $FILE && \
#    mv android-ndk-${ANDROID_NDK_VERSION} /opt/android-ndk && \
#    rm android-ndk-${ANDROID_NDK_VERSION}-linux-x86_64.zip
#ENV ANDROID_NDK_HOME /opt/android-ndk

# Install CrystaX NDK
RUN CHECKSUM=7305b59a3cee178a58eeee86fe78ad7bef7060c6d22cdb027e8d68157356c4c0 && \
    FILE=crystax-ndk-10.3.2-linux-x86_64.tar.xz && \
    curl -sLo $FILE https://www.crystax.net/download/$FILE && \
    openssl sha256 ${FILE} > $$.file && \
    echo "SHA256(${FILE})= ${CHECKSUM}" > $$.expected && \
    diff $$.file $$.expected && \
    echo 'OK' || echo '*** CORRUPTED!!!'

RUN tar xf crystax-ndk-10.3.2-linux-x86_64.tar.xz -C /opt
ENV ANDROID_NDK_HOME /opt/crystax-ndk-10.3.2

# download and install Gradle
ENV GRADLE_VERSION 4.3
RUN cd /opt && \
    FILE=gradle-${GRADLE_VERSION}-bin.zip && \
    curl -sLo $FILE -q https://services.gradle.org/distributions/$FILE && \
    unzip -q $FILE && \
    mv gradle-${GRADLE_VERSION} gradle && \
    rm gradle*.zip
ENV GRADLE_HOME /opt/gradle

# Environment variables
ENV ANDROID_SDK_HOME $ANDROID_HOME

ENV PATH ${INFER_HOME}/bin:${PATH}
ENV PATH $PATH:$ANDROID_SDK_HOME/tools
ENV PATH $PATH:$ANDROID_SDK_HOME/tools/bin
ENV PATH $PATH:$ANDROID_SDK_HOME/platform-tools
#ENV PATH $PATH:$ANDROID_SDK_HOME/build-tools/26.0.2
#ENV PATH $PATH:$ANDROID_SDK_HOME/build-tools/25.0.3
ENV PATH $PATH:$ANDROID_SDK_HOME/build-tools/21.1.2
ENV PATH $PATH:$ANDROID_NDK_HOME
ENV PATH $PATH:$JAVA_HOME/bin
ENV PATH $PATH:$GRADLE_HOME/bin

# Support Gradle
ENV TERM dumb
ENV JAVA_OPTS "-Xms4096m -Xmx4096m"
ENV GRADLE_OPTS "-XX:+UseG1GC -XX:MaxGCPauseMillis=1000"

RUN mkdir -p $ANDROID_HOME/licenses && \
    echo "\n8933bad161af4178b1185d1a37fbf41ea5269c55" > $ANDROID_HOME/licenses/android-sdk-license && \
    echo "\nd56f5187479451eabf01fb78af6dfcb131a6481e" >> $ANDROID_HOME/licenses/android-sdk-license && \
    echo "\ne6b7c2ab7fa2298c15165e9583d0acf0b04a2232" >> $ANDROID_HOME/licenses/android-sdk-license && \
    echo "\n84831b9409646a918e30573bab4c9c91346d8abd" > $ANDROID_HOME/licenses/android-sdk-preview-license && \
    echo "\nd975f751698a77b662f1254ddbeed3901e976f5a" > $ANDROID_HOME/licenses/intel-android-extra-license

RUN mkdir -p ~/.android $ANDROID_HOME/.android && \
    touch ~/.android/repositories.cfg $ANDROID_HOME/.android/repositories.cfg

# FIXME: This seems redundant
RUN $ANDROID_HOME/tools/bin/sdkmanager "build-tools;21.1.2"
RUN $ANDROID_HOME/tools/bin/sdkmanager "platforms;android-21"
RUN $ANDROID_HOME/tools/bin/sdkmanager "platform-tools"

# Updating everything again
#RUN yes | sdkmanager --update
#RUN yes | sdkmanager --licenses

RUN apt-get update && \
    apt-get install -yq \
      ant python3-pip git zlib1g-dev

RUN git clone https://github.com/kivy/python-for-android.git /python-for-android
WORKDIR /python-for-android
RUN python3 setup.py install

RUN pip3 install --upgrade pip
RUN pip3 install django
RUN pip3 install virtualenv
RUN pip install Cython

RUN pip3 install djangoforandroid
#RUN git clone https://bitbucket.org/djangoforandroid/django-for-android /django-for-android
#WORKDIR /django-for-android
#RUN python3 setup.py install

RUN $ANDROID_HOME/tools/bin/sdkmanager --list | sed -e '/Available Packages/q'

# This is for aapt in the android sdk build tools to run correctly
RUN dpkg --add-architecture i386
RUN apt-get -qqy update
RUN apt-get -qqy install libncurses5:i386 libstdc++6:i386 zlib1g:i386

ADD . /app

WORKDIR /app

RUN python3 manage.py androidcreate
RUN python3 manage.py androidapk

RUN find / -name '*.apk' -print

VOLUME /outputs

RUN find / -name '*.apk' -print
CMD cp *.apk /outputs

