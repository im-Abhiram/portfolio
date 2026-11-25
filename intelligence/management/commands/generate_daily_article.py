import json
from datetime import datetime
from django.core.management.base import BaseCommand
from intelligence.generator import generate_daily_article, get_local_date
from ai_services.gemini import get_gemini_config


class Command(BaseCommand):
    help = "Generate today's NETWORK INTELLIGENCE technical article via Gemini API (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Target scheduled date in YYYY-MM-DD format (defaults to today in configured timezone).'
        )
        parser.add_argument(
            '--topic',
            type=str,
            help='Optional explicit topic override.'
        )
        parser.add_argument(
            '--mode',
            type=str,
            choices=['auto', 'review', 'manual'],
            help='Override publish mode (auto, review, or manual).'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Select topic and print execution plan without calling Gemini or writing DB.'
        )
        parser.add_argument(
            '--export-json',
            type=str,
            help='Optional file path to export generated structured JSON for manual server import.'
        )

    def handle(self, *args, **options):
        cfg = get_gemini_config()
        if not cfg['daily_article_enabled'] and not options.get('dry_run'):
            self.stdout.write(self.style.WARNING(
                "Daily article generation is currently disabled via GEMINI_DAILY_ARTICLE_ENABLED / AISettings."
            ))
            return

        target_date = None
        if options.get('date'):
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stderr.write(self.style.ERROR("Invalid --date format. Use YYYY-MM-DD."))
                return
        else:
            target_date = get_local_date(cfg.get('timezone'))

        result = generate_daily_article(
            target_date=target_date,
            explicit_topic=options.get('topic'),
            publish_mode=options.get('mode'),
            dry_run=bool(options.get('dry_run')),
        )

        status = result.get('status')
        message = result.get('message', '')

        if status == 'success':
            article = result['article']
            self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))
            if options.get('export_json'):
                payload = {
                    'title': article.title,
                    'subtitle': article.subtitle,
                    'introduction': article.introduction,
                    'category': article.category,
                    'tags': article.get_tags_list(),
                    'reading_time': article.reading_time,
                    'ai_generated': article.ai_generated,
                    **article.content,
                }
                with open(options['export_json'], 'w', encoding='utf-8') as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)
                self.stdout.write(self.style.SUCCESS(f"[EXPORTED] Saved JSON to {options['export_json']}"))
        elif status == 'skipped':
            self.stdout.write(self.style.WARNING(f"[SKIPPED] {message}"))
        elif status == 'dry_run':
            self.stdout.write(self.style.NOTICE(f"[DRY RUN] {message}"))
        elif status == 'duplicate_blocked':
            self.stdout.write(self.style.WARNING(f"[DUPLICATE BLOCKED] {message}"))
        else:
            self.stderr.write(self.style.ERROR(f"[FAILED] {message}"))
