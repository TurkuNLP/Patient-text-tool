cd /home/appuser/
./solr-7.5.0/bin/solr start
cd search_app
#bundle install
rails server &
#CMD pip3 install -U -r /home/appuser/solrglue/requirements.txt
cd ../solrglue
python3 -m flask run --host=0.0.0.0
