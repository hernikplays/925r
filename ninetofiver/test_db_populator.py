from calendar import monthrange
import datetime
from itertools import product
import logging
import random

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django_countries import countries

from ninetofiver.models import Timesheet, WorkSchedule, Leave, LeaveType, LeaveDate, Company, ContractGroup,\
    ContractRole, ContractUser, ProjectContract, SupportContract, PerformanceType, ActivityPerformance, Location,\
    ConsultancyContract, ApiKey, ContractLogType, EmploymentContractType, EmploymentContract, Holiday, Whereabout, \
    TrainingType, Invoice, UserTraining, Training

log = logging.getLogger(__name__)


def get_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    return random_date


def get_random_datetime(start_datetime, end_datetime):
    time_between_dates = end_datetime - start_datetime
    minutes_between_dates = time_between_dates.seconds // 60

    random_number_of_minutes = random.randrange(minutes_between_dates)
    random_datetime = start_datetime + datetime.timedelta(minutes=random_number_of_minutes)

    return random_datetime


def xprint(*args, **kwargs):
    print(" ".join(map(str, args)), **kwargs)


class TestDBPupulator:
    def __init__(self, default_size, perf_tables_size):
        if not settings.DEBUG:
            log.error('settings.DEBUG is False. Aborting')
            exit(1)

        self.default_range = range(1, default_size + 1)
        self.perf_tables_range = range(1, perf_tables_size + 1)
        self.activity_performances = []
        self.api_keys = []
        self.companies = []
        self.companies_customers = []
        self.contract_groups = []
        self.contract_log_types = []
        self.contract_roles = []
        self.contract_users = []
        self.contracts = []
        self.employment_contract = []
        self.employment_contract_type = []
        self.holidays = []
        self.invoices = []
        self.leavedates = []
        self.leaves = []
        self.leavetypes = []
        self.locations = []
        self.perf_types = []
        self.timesheets = []
        self.training_types = []
        self.user_trainings = []
        self.trainings = []
        self.users = []
        self.whereabouts = []
        self.work_schedules = []

    def execute(self):
        ''' Order of methods is important '''
        self._populate_basic_tables()
        self._populate_performance_tables()
        self._populate_leave_tables()
        self._populate_additional_tables()

    def _populate_basic_tables(self):
        '''
        This fills basic tables with data for debugging purposes
        when modifying, make sure to change all lists related to the object
        '''
        xprint("Populate basic tables")

        self.leavetypes = [
            ('Vacation', 'vacation', False, False),
            ('Sickness', 'sickness', False, True),
            ('Recup', 'recup', True, False),
            ('Unpaid', 'unpaid', False, False),
        ]
        for leave_name, leave_desc, leave_overtime, leave_sickness in self.leavetypes:
            lt = LeaveType(
                name=leave_name,
                description=leave_desc,
                overtime=leave_overtime,
                sickness=leave_sickness
            )
            lt.save()
        xprint(" - LeaveType:", len(self.leavetypes))

        companies_example = [
            ('Inuits', 'CZ12345678', 'Zamenhofova 150 00 Praha 5', 'CZ', True),
            ('ABC', 'BE12345678', 'Ocean drive 42 2060 Antwerpen', 'BE', False),
        ]
        for company_name, company_vat, company_addr, company_country, company_internal in companies_example:
            com = Company(
                name=company_name,
                vat_identification_number=company_vat,
                address=company_addr,
                country=company_country,
                internal=company_internal
            )
            com.save()
            self.companies.append(com)
        xprint(" - Company:", len(self.companies))

        locations_examples = ['Home', 'Brasschaat HQ', 'Ghent', 'Hasselt', 'Prague', 'Brno', 'Kraków', 'Kiev']
        for loc_name in locations_examples:
            loc = Location(
                name=loc_name
            )
            loc.save()
            self.locations.append(loc)
        xprint(" - Location:", len(self.locations))

        perf_types_example = [
            ('Minimal', 'minimal', 0.50),
            ('Normal', 'normal', 1.00),
            ('Overtime', 'overtime', 1.50),
            ('Overtime', 'overtime', 2.00),
        ]
        for pt_name, pt_description, pt_multiplier in perf_types_example:
            pt = PerformanceType(
                name=pt_name,
                description=pt_description,
                multiplier=pt_multiplier
            )
            pt.save()
            self.perf_types.append(pt)
        xprint(" - PerformanceType:", len(self.perf_types))

        work_schedules_example = [
            ('Fulltime (7.6h/day)', 7.60, 7.60, 7.60, 7.60, 7.60, 0.00, 0.00),
            ('Parttime (6.4h/day)', 6.40, 6.40, 6.40, 6.40, 6.40, 0.00, 0.00),
            ('Zero', 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        ]
        for ws_name, ws_mon, ws_tue, ws_wed, ws_thu, ws_fri, ws_sat, ws_sun in work_schedules_example:
            ws = WorkSchedule(
                name=ws_name,
                monday=ws_mon,
                tuesday=ws_tue,
                wednesday=ws_wed,
                thursday=ws_thu,
                friday=ws_fri,
                saturday=ws_sat,
                sunday=ws_sun
            )
            ws.save()
            self.work_schedules.append(ws)
        xprint(" - WorkSchedule:", len(self.work_schedules))

    def _populate_performance_tables(self):
        '''
        Fills higher amount of test data to all contract/performance-related tables
        Populate db with users, companies, customers, contract_groups
        '''
        xprint("Populate performance tables")

        for i in self.default_range:
            cr = ContractRole(
                name="Contract role " + str(i),
                description="Description for contract role",
            )
            self.contract_roles.append(cr)
        # For more information about when and how to use bulk_create method follow the link:
        # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#bulk-create
        ContractRole.objects.bulk_create(self.contract_roles)
        xprint(" - ContractRole:", len(self.contract_roles))

        # Its ok to have smaller no. of records for these tables
        for i in self.default_range:
            usr = User(
                username='test_user_' + str(i),
                email='test_' + str(i) + '@mail.com',
                first_name="User" + str(i),
                last_name="Inuit",
                is_active=random.choice([True, True, True, False]),
            )
            usr.save()
            self.users.append(usr)

            comp = Company(
                vat_identification_number='CZ00' + str(i),
                name='test_company_' + str(i),
                address='test_company_' + str(i),
                country='CZ',
                internal=True,
            )
            comp.full_clean()
            comp.save()
            self.companies.append(comp)

            comp_cust = Company(
                vat_identification_number='CZ000' + str(i),
                name='test_company_customer_' + str(i),
                address='test_company_customer_' + str(i),
                country='CZ',
                internal=False,
            )
            comp_cust.full_clean()
            comp_cust.save()
            self.companies_customers.append(comp_cust)

            cg = ContractGroup(
                name='test_contract_group_' + str(i)
            )
            cg.save()
            self.contract_groups.append(cg)

        xprint(" - User:", len(self.users))
        xprint(" - Company:", len(self.companies))
        xprint(" - ContractGroup:", len(self.contract_groups))

        # populate contracts & activity performances -> higher number of records is good
        for x in self.perf_tables_range:
            proj_cont = ProjectContract(
                name='test_project_contract_' + str(x),
                description='Test project contract ' + str(x),
                customer=self.companies_customers[random.randrange(len(self.companies_customers))],
                company=self.companies[random.randrange(len(self.companies))],
                starts_at=get_random_date(datetime.date(2017, 1, 1), datetime.date(2021, 1, 1)),
                ends_at=get_random_date(datetime.date(2021, 9, 9), datetime.date(2030, 1, 1)),
                active=1,
                fixed_fee=round(random.uniform(0, 1000), 2),
            )

            cons_cont = ConsultancyContract(
                name='test_consultancy_contract_' + str(x),
                description='Test consultancy contract ' + str(x),
                customer=self.companies_customers[random.randrange(len(self.companies_customers))],
                company=self.companies[random.randrange(len(self.companies))],
                starts_at=get_random_date(datetime.date(2017, 1, 1), datetime.date(2021, 1, 1)),
                ends_at=get_random_date(datetime.date(2021, 9, 9), datetime.date(2030, 1, 1)),
                active=1,
                duration=round(random.uniform(0, 100), 1),
                day_rate=round(random.uniform(0, 100), 2),
            )

            supp_cont = SupportContract(
                name='test_support_contract_' + str(x),
                description='Test support contract ' + str(x),
                customer=self.companies_customers[random.randrange(len(self.companies_customers))],
                company=self.companies[random.randrange(len(self.companies))],
                starts_at=get_random_date(datetime.date(2017, 1, 1), datetime.date(2021, 1, 1)),
                ends_at=get_random_date(datetime.date(2021, 9, 9), datetime.date(2030, 1, 1)),
                active=1,
                day_rate=round(random.uniform(0, 100), 2),
                fixed_fee=round(random.uniform(0, 1000), 2),
            )

            proj_cont.save()
            cons_cont.save()
            supp_cont.save()
            self.contracts.append(proj_cont)
            self.contracts.append(cons_cont)
            self.contracts.append(supp_cont)
        xprint(" - Contract:", len(self.contracts))

        # add contract users
        self.contract_roles = ContractRole.objects.all()
        for item in product(self.users, self.contracts):
            cu = ContractUser(
                user=item[0],
                contract=item[1],
                contract_role=self.contract_roles[0],
            )
            self.contract_users.append(cu)
        ContractUser.objects.bulk_create(self.contract_users)
        xprint(" - ContractUser:", len(self.contract_users))

        self.create_timesheets()

        # add performance
        # 10 for every timesheet, random contracts
        for ts in self.timesheets:
            for x in range(1, 11):
                days_in_month = monthrange(ts.year, ts.month)[1]

                act_perf = ActivityPerformance(
                    timesheet=ts,
                    date=datetime.date(ts.year, ts.month, random.randint(1, days_in_month)),
                    contract=self.contracts[random.randrange(len(self.contracts))],
                    performance_type=self.perf_types[1],
                    contract_role=self.contract_roles[0],
                    description='test_activity_performance_' + str(x),
                    duration=1,
                )
                act_perf.save()
                self.activity_performances.append(act_perf)
        xprint(" - ActivityPerformance:", len(self.activity_performances))

    def create_timesheets(self):
        """Create a new timesheet for the current month for each user."""
        today = datetime.date.today()
        next_month = datetime.date.today() + relativedelta(months=1)

        for user in self.users:
            # Ensure timesheet for this month exists
            ts_this_month, _ = Timesheet.objects.get_or_create(
                user=user,
                month=today.month,
                year=today.year
            )

            # Ensure timesheet for next month exists
            ts_next_month, _ = Timesheet.objects.get_or_create(
                user=user,
                month=next_month.month,
                year=next_month.year
            )

            self.timesheets.append(ts_this_month)
            self.timesheets.append(ts_next_month)
        xprint(" - Timesheet:", len(self.timesheets))

    def _populate_leave_tables(self):
        # Fills higher amount of test data to all leave-related tables
        xprint("Populate leave tables")

        for usr in self.users:
            leave_dates_for_user = []
            for x in range(1, 3):
                lv = Leave(
                    user=usr,
                    leave_type=LeaveType.objects.get(name='Vacation'),
                    description='vacation_test',
                )
                lv.save()
                self.leaves.append(lv)

                # leave length in days
                leave_length = 3

                # load all timesheets for user
                timesheets_for_user = Timesheet.objects.filter(user=usr)
                # select one timesheet for user
                ts = timesheets_for_user[random.randrange(len(timesheets_for_user))]
                k = True
                while k is True:
                    invalid_date_found = False
                    # find a leave date in selected timesheet
                    start_date = get_random_date(datetime.datetime(ts.year, ts.month, 1),
                                                 # potential end date
                                                 datetime.datetime(ts.year, ts.month, 1)
                                                 + relativedelta(months=1)
                                                 - datetime.timedelta(days=leave_length))  # unknown no. of days in mth
                    # check if user already has leave planned in this date. if so, find another date
                    for pot_day_no in range(0, leave_length):
                        potential_leave_date = start_date + datetime.timedelta(days=pot_day_no)
                        if potential_leave_date not in leave_dates_for_user:
                            continue
                        else:
                            invalid_date_found = True
                            break
                    if invalid_date_found is True:
                        continue
                    else:
                        break

                for day in range(0, leave_length):
                    ld = LeaveDate(
                        leave=lv,
                        timesheet=ts,
                        starts_at=start_date.replace(hour=9, minute=00, second=00) + datetime.timedelta(days=day),
                        ends_at=start_date.replace(hour=17, minute=00, second=00) + datetime.timedelta(days=day),
                    )
                    # adding each day of user's holiday to the list so that holidays never collide
                    leave_dates_for_user.append(start_date + datetime.timedelta(days=day))
                    ld.save()
                    self.leavedates.append(ld)
        xprint(" - Leave:", len(self.leaves))
        xprint(" - LeaveDate:", len(self.leavedates))

    def _populate_additional_tables(self):
        xprint("Populate additional tables")

        for i, user in enumerate(self.users):
            ak = ApiKey(
                name="API test key " + str(i),
                user=user,
            )
            ak.save()
            self.api_keys.append(ak)
        xprint(" - ApiKey:", len(self.api_keys))

        # in one loop ContractLogType, EmploymentContractType, Holiday, Whereabout
        for i in self.default_range:
            clt = ContractLogType(
                name="Contract log type " + str(i),
            )
            clt.save()
            self.contract_log_types.append(clt)

            ect = EmploymentContractType(
                name="Employment contract type " + str(i),
            )
            ect.save()
            self.employment_contract_type.append(ect)

            ho = Holiday(
                name="Holiday " + str(i),
                date=get_random_date(datetime.date(2017, 1, 1), datetime.date(2030, 1, 1)),
                country=(list(countries)[random.randrange(len(countries))])[0],  # random country code from countries
            )
            ho.save()
            self.holidays.append(ho)

            tsheet = self.timesheets[i % len(self.timesheets)]

            wa = Whereabout(
                timesheet=tsheet,
                location=self.locations[i % len(self.locations)],
                starts_at=get_random_datetime(
                    datetime.datetime(tsheet.year, tsheet.month, 1, 0, 0),
                    datetime.datetime(tsheet.year, tsheet.month, 1, 11, 59)),
                ends_at=get_random_datetime(
                    datetime.datetime(tsheet.year, tsheet.month, 1, 12, 0),
                    datetime.datetime(tsheet.year, tsheet.month, 1, 23, 59)),
            )
            wa.save()
            self.whereabouts.append(wa)

        xprint(" - ContractLogType:", len(self.contract_log_types))
        xprint(" - EmploymentContractType:", len(self.employment_contract_type))
        xprint(" - Holiday:", len(self.holidays))
        xprint(" - Whereabout:", len(self.whereabouts))

        for i, user in enumerate(self.users):
            company_index = i % len(self.companies)
            company = self.companies[company_index]
            prev_company = self.companies[company_index - 1 if company_index > 0 else len(self.companies)-1] # grab another company so we can create an expired contract
            
            if not company.internal:
                continue
            while not prev_company.internal:
                company_index = company_index - 1 if company_index > 0 else len(self.companies)-1
                prev_company = self.companies[company_index]
            ec = EmploymentContract(
                user=user,
                company=company,
                employment_contract_type=self.employment_contract_type[i % len(self.employment_contract_type)],
                work_schedule=self.work_schedules[i % len(self.work_schedules)],
                started_at=get_random_date(datetime.date(2021, 1, 2), datetime.date(2024, 1, 1)),
                ended_at=get_random_date(datetime.date(2024, 2, 2), datetime.date(2030, 1, 1)),
            )
            ec.save()

            ec_exp = EmploymentContract(
                user=user,
                company=prev_company,
                employment_contract_type=self.employment_contract_type[i % len(self.employment_contract_type)],
                work_schedule=self.work_schedules[i % len(self.work_schedules)],
                started_at=get_random_date(datetime.date(2012, 1, 1), datetime.date(2018, 1, 1)),
                ended_at=get_random_date(datetime.date(2018, 2, 2), datetime.date(2021, 1, 1)),
            )
            ec_exp.save() # save an expired contract
            self.employment_contract.append(ec)
            self.employment_contract.append(ec_exp)
        xprint(" - EmploymentContract:", len(self.employment_contract))

        for contract in self.contracts:
            inv = Invoice(
                contract=contract,
                period_starts_at=get_random_date(datetime.date(2017, 1, 1), datetime.date(2021, 1, 1)),
                period_ends_at=get_random_date(datetime.date(2021, 2, 2), datetime.date(2030, 1, 1)),
                date=get_random_date(datetime.date(2021, 2, 2), datetime.date(2030, 1, 1)),
                reference="Some reference",
                description="Description info",
            )
            inv.save()
            self.invoices.append(ec)
        xprint(" - Invoice:", len(self.invoices))

        for i in range(1, 11):
            tt = TrainingType(
                name="Training type " + str(i),
                country=(list(countries)[random.randrange(len(countries))])[0],  # random country code from countries
                description="Description of training type",
            )
            tt.save()
            self.training_types.append(tt)
        xprint(" - TrainingType:", len(self.training_types))

        for user in self.users:
            ut = UserTraining(
                user = user
            )
            ut.save()
            self.user_trainings.append(ut)
        xprint(" - UserTraining:", len(self.user_trainings))

        for i in range(1, 20):
            training = Training(
                user_training = random.choice(self.user_trainings),
                training_type = random.choice(self.training_types)
            )
            training.save()
            self.trainings.append(training)
        xprint(" - Training:", len(self.trainings))
        
        # add birth_date to users in user_info table
        for user in self.users:
            user.userinfo.birth_date = get_random_date(datetime.date(1970, 1, 1), datetime.date(2005, 1, 1))
            user.userinfo.save()
        xprint(" - Userinfo: birth_dates added")