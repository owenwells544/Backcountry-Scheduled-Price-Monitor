import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from price_monitor import PriceMonitorSpider

def parse_args():
    parser = argparse.ArgumentParser(
        description='Schedule price monitor spider runs',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    #default runtime of 8 am
    parser.add_argument(
        '--hour', 
        type=int, 
        default=8, 
        help='scheduler int hour arg (military time)'
    )
    parser.add_argument(
        '--minute', 
        type=int, 
        default=0, 
        help='scheduler int minute arg'
    )
    
    parser.add_argument(
        '--keywords',
        type=lambda s: [item.strip() for item in s.split(',')],
        default = [],
        help='keywords list ie: --keywords "climbing,shoes"'
    )
    
    # Return the parsed arguments
    return parser.parse_args()

def run_spider(keywords=None):
    print("started scraping")

    #create and run spider process (blocking)
    process = CrawlerProcess(get_project_settings())
    process.crawl(PriceMonitorSpider, keywords=keywords)
    process.start()
    
    print("finished scraping")

def main():
    args = parse_args()
    
    scheduler = BlockingScheduler()
    
    scheduler.add_job(
        run_spider,
        trigger=CronTrigger(hour=args.hour, minute=args.minute), #here is the field where the daily runtime is specificied,
        #in hours and minutes using military time
        kwargs={'keywords': args.keywords},  
        id='price_monitor_job',
        name='Check prices on backcountry.com daily',
        max_instances=1,
        coalesce=True
    )
    
    print("Scheduler started")

    #ctrl c keyboard interrupt does not work, have not been able to find fix
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped")

if __name__ == "__main__":
    main()