class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def generate_daily_report(self, date):
        stats = self.db_manager.get_detection_counts(date)
        total_detections = sum(stats.values())
        
        report = f"检测报告 - {date}\n"
        report += f"总检测次数: {total_detections}\n\n"
        
        for class_name, count in stats.items():
            percentage = (count / total_detections) * 100
            report += f"{class_name}: {count} ({percentage:.1f}%)\n"
            
        return report 