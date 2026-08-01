from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        try:
            from rest_framework import serializers
            
            _orig_to_internal_value = serializers.DecimalField.to_internal_value

            def auto_rounded_to_internal_value(self, data):
                if data is not None and data != '':
                    try:
                        val = Decimal(str(data))
                        places = self.decimal_places if self.decimal_places is not None else 6
                        exponent = Decimal('10') ** -places
                        val = val.quantize(exponent, rounding=ROUND_HALF_UP)
                        data = str(val)
                    except (InvalidOperation, TypeError, ValueError):
                        pass
                return _orig_to_internal_value(self, data)

            serializers.DecimalField.to_internal_value = auto_rounded_to_internal_value
        except Exception:
            pass

