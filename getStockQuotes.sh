echo Start >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
date >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
cd /mnt/usbmain/Jonathan/Projects/Bandwagon
python getstockquotes.py > detail.log
cp stocks.html /var/www/bandwagon/index.html
echo Stop >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
date >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
