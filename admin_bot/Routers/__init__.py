from .AdminRouters.MailingRouter.mail_router import MailRouter
from .AdminRouters.ReplySuggestionRouter.reply_suggestion_router import RepSuggestionRouter
from .AdminRouters.RoleRouter.role_router import RoleRouter
from .UserRouters.ScheduleRouter.main_schedule_router import ScheduleRouter
from .UserRouters.SettingsRouter.change_faculty_suggestions_router import SettingsRouter
from .UserRouters.StartRouter.start import StartRouter
from .UserRouters.StartRouter.registration import RegistrationRouter



# Список всех роутеров для экспорта
__all__ = [
    'MailRouter', 'RepSuggestionRouter', 'RoleRouter', 'RegistrationRouter',
    'ScheduleRouter', 'SettingsRouter', 'StartRouter'
]
