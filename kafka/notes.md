sudo apt-get update
sudo apt-get install default-jre
sudo apt-get install zookeeperd

# check installation of zookeeper
telnet localhost 2181
# enter `ruok` when prompted, reply should be `imok`

# add a system user for kafka
sudo adduser kafka
# add it to sudo group
sudo adduser kafka sudo
# change user to kafka
su -l kafka
# download kafka files
mkdir ~/Downloads
curl "https://downloads.apache.org/kafka/2.6.2/kafka_2.13-2.6.2.tgz" -o ~/Downloads/kafka.tgz
mkdir ~/kafka && cd ~/kafka
tar -xvzf ~/Downloads/kafka.tgz --strip 1

# post extraction dir structure should be like:
~kafka/kafka/   logs        # create this logs folder manually
                bin
                config
                kafka.log
                libs
                LICENSE
                licenses
                logs
                NOTICE
                site-docs

# edit kafka server properties file
nano ~/kafka/config/server.properties
# add this line at the bottom
delete.topic.enable = true
# change logs directory
log.dirs=/home/kafka/kafka/logs

# Create systemd unit file for Zookeeper
sudo nano /etc/systemd/system/zookeeper.service
# write the below
[Unit]
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=kafka
ExecStart=/home/kafka/kafka/bin/zookeeper-server-start.sh /home/kafka/kafka/config/zookeeper.properties
ExecStop=/home/kafka/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target



# create a Kafka systemd unit file
sudo nano /etc/systemd/system/kafka.service
# write the below
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=kafka
ExecStart=/bin/sh -c '/home/kafka/kafka/bin/kafka-server-start.sh /home/kafka/kafka/config/server.properties > /home/kafka/kafka/kafka.log 2>&1'
ExecStop=/home/kafka/kafka/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target


# command to start kafka
sudo systemctl start kafka
# command to stop kafka
sudo systemctl stop kafka
# check kafka status
sudo systemctl status kafka
# enable services to be started with the server
sudo systemctl enable zookeeper
sudo systemctl enable kafka


# create a topic in kafka
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic TutorialTopic

# list topics in kafka
 ~/kafka/bin/kafka-topics.sh --bootstrap-server 192.168.137.185:9092 --list
    OR
 ~kafka/bin/kafka-topics.sh --list --zookeeper localhost:2181

# start a terminal producer session
~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test

# start a terminal consumer session
~/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
# the `--from-begininning` parameter receives all the messages in the channel from the begining

# to use kafka in python
# install kafka package
pip install kafka-python


# sample producer code
from time import sleep  
from json import dumps  
from kafka import KafkaProducer

my_producer = KafkaProducer(  
    bootstrap_servers = ['localhost:9092'],  
    value_serializer = lambda x:dumps(x).encode('utf-8')  
    )  

for n in range(500):  
    my_data = {'num' : n}  
    my_producer.send('test', value = my_data)  
    sleep(5)  


# sample consumer code
from json import loads  
from kafka import KafkaConsumer  

my_consumer = KafkaConsumer('test', bootstrap_servers = ['localhost : 9092']
                            , value_deserializer = lambda x : loads(x.decode('utf-8'))    
                            )

for message in my_consumer:  
    message = message.value
    print(message)



# list topics in kafka
~/kafka/bin/kafka-topics.sh --list --zookeeper localhost:2181

# to delete a topic
~/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --delete --topic test

# remove all messages from all topics
sudo systemctl stop kafka
sudo systemctl stop zookeeper
rm -R ~/kafka/logs
mkdir ~/kafka/logs
sudo systemctl start zookeeper
sudo systemctl status zookeeper

