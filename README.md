# task-queue-dispatcher
Transport between postgres and gearman which uses notifications. In purposes of organization asynchronous code in python gevent lib is used.

# Instalation

All requirements are contains in requirements/production.txt file and could be installed by

pip install -r requirements/production.txt

# Run

Server could be run by
python process.py <options> command

# Options

-p, --processor - class processor for deamon. Currently there is only one processor GearmanTransport
-q, --queue-name - table name for listening
-c, --chunk - chunk number for building horizontal scalability transport
-l, --logfile - file for log

# Example of queue table

CREATE TABLE <queue_name>_<chunk> (
  id int,
  payload json NOT NULL, # body of task to be transfered into queue
  sked_time timestamp with time zone, # when to transfer task into queue
  CONSTRAINT gearman_transport_1_pkey PRIMARY KEY (id)
)

