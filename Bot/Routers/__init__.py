from .AdminRouters.MailingRouter.mail_router import MailRouter
from .AdminRouters.ReplySuggestionRouter.reply_suggestion_router import RepSuggestionRouter
from .AdminRouters.RoleRouter.role_router import RoleRouter
from .UserRouters.MenuRouter.menu_router import MenuRouter
from .UserRouters.ScheduleRouter.temp_week_schedule_router import ScheduleRouter
from .UserRouters.SettingsRouter.change_group_suggestions_router import SettingsRouter
from .UserRouters.StartRouter.start import StartRouter
from .UserRouters.StartRouter.registration import RegistrationRouter
from .UserRouters.NotificationRouter.notification_router import NotificationRouter
from .AdminRouters.AddScheduleVucRouter.add_schedule_vuc_router import AddScheduleVucRouter
from .UserRouters.MenuRouter.SubRouters.vuc_router import VucRouter

# Список всех роутеров для экспорта
__all__ = [
    'MailRouter', 'RepSuggestionRouter', 'RoleRouter', 'RegistrationRouter', 'AddScheduleVucRouter',
    'MenuRouter', 'ScheduleRouter', 'SettingsRouter', 'StartRouter', 'NotificationRouter', 'VucRouter'
]
