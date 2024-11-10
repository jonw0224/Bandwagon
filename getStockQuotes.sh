echo Start >> /mnt/share/Jonathan/Projects/Bandwagon/cron.log
date >> /mnt/share/Jonathan/Projects/Bandwagon/cron.log
cd /mnt/share/Jonathan/Projects/Bandwagon
python getstockquotes.py
date >> /mnt/share/Jonathan/Projects/Bandwagon/cron.log
