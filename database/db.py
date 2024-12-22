import motor.motor_asyncio
from datetime import datetime
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db.users
        self.wallet_col = self.db.wallet
        self.earnings_col = self.db.earnings  # Earnings collection for tracking
        self.tasks_col = self.db.tasks  # Tasks collection for tracking user tasks
        self.task_time_col = self.db.task_time  # Collection for task done times by domain

     
    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            session=None,
            state=None,
            country=None,
            ip_address=None,
            invited=[],  # List to store the IDs of users invited by this user
        )
    
    def new_wallet(self, id):
        return dict(
            id=id,
            balance=0.0,  # Default balance as a float
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        wallet = self.new_wallet(id)
        await self.users_col.insert_one(user)
        await self.wallet_col.insert_one(wallet)
    
    async def add_user_ip(self, user_id, ip_address, state, country):
        """Add user's IP address, state, and country."""
        await self.users_col.update_one(
            {'id': int(user_id)},
            {'$set': {'ip_address': ip_address, 'state': state, 'country': country}}
        )
    
    async def is_user_exist(self, id):
        user = await self.users_col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.users_col.count_documents({})
        return count

    async def get_all_users(self):
        return self.users_col.find({})

    async def delete_user(self, user_id):
        await self.users_col.delete_many({'id': int(user_id)})
        await self.wallet_col.delete_many({'id': int(user_id)})
        await self.earnings_col.delete_many({'user_id': int(user_id)})
        await self.tasks_col.delete_many({'user_id': int(user_id)})

    async def set_session(self, id, session):
        await self.users_col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.users_col.find_one({'id': int(id)})
        return user['session']

    # Wallet Functions

    async def get_all_due(self):
        total = 0.0
        async for wallet in self.wallet_col.find({}):
            total += wallet['balance']
        return total

    async def get_balance(self, user_id):
        wallet = await self.wallet_col.find_one({'id': int(user_id)})
        if wallet:
            return wallet['balance']
        return None

    async def give_coin(self, amount, user_id):
        """Add coins (including decimals) to a user's wallet and log earnings."""
        await self.wallet_col.update_one(
            {'id': int(user_id)},
            {'$inc': {'balance': float(amount)}}
        )
        await self.earnings_col.insert_one({
            'user_id': int(user_id),
            'amount': float(amount),
            'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'earn'
        })

    async def withdraw_coin(self, amount, user_id):
        """Subtract coins (including decimals) from a user's wallet."""
        wallet = await self.wallet_col.find_one({'id': int(user_id)})
        if wallet and wallet['balance'] >= float(amount):
            await self.wallet_col.update_one(
                {'id': int(user_id)},
                {'$inc': {'balance': -float(amount)}}
            )
        else:
            raise ValueError("Insufficient balance.")

    async def get_top_users(self):
        """Retrieve the top 10 users with the highest wallet balances."""
        cursor = self.wallet_col.find({}).sort('balance', -1).limit(10)
        top_users = []
        async for wallet in cursor:
            top_users.append({'id': wallet['id'], 'balance': wallet['balance']})
        return top_users

    async def get_user_earnings(self, user_id):
        """Retrieve all earnings of a user."""
        cursor = self.earnings_col.find({'user_id': int(user_id)})
        earnings = []
        async for earning in cursor:
            earnings.append(earning)
        return earnings

    # New Functions for Inviting Users

    async def one_invited(self, inviter_id, invitee_id):
        """Add a user to the inviter's 'invited' list."""
        await self.users_col.update_one(
            {'id': int(inviter_id)},
            {'$addToSet': {'invited': int(invitee_id)}}
        )

    async def get_inviter(self, user_id):
        """
        Retrieve the inviter ID of a specific user.
        """
        # Search for a user whose 'invited' list contains the given user_id
        inviter = await self.users_col.find_one({'invited': int(user_id)}, {'id': 1})
        if inviter:
            return inviter['id']
        return None  # Return None if no inviter found

    async def total_invited(self, user_id):
        """Return the total number of users invited by a specific user."""
        user = await self.users_col.find_one({'id': int(user_id)})
        if user:
            return len(user['invited'])
        return 0

    async def top_invitors(self):
        """Retrieve the top 10 users with the most invitations."""
        cursor = self.users_col.find({}).sort('invited', -1).limit(10)
        top_invitors = []
        async for user in cursor:
            top_invitors.append({
                'id': user['id'],
                'invited_count': len(user['invited'])
            })
        return top_invitors

    # New Functions for Tracking Tasks

    async def task_done(self, user_id):
        """Log a task completion by a user."""
        task_data = {
            'user_id': int(user_id),
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
        }
        await self.tasks_col.insert_one(task_data)

    async def total_task_done(self, date):
        """Get the total tasks completed on a specific date."""
        date_str = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        count = await self.tasks_col.count_documents({'date': date_str})
        return count

    async def off_task(self, x):
        """Get users who have completed less than x tasks."""
        users_with_few_tasks = []
        async for user in self.users_col.find({}):
            task_count = await self.tasks_col.count_documents({'user_id': user['id']})
            if task_count < x:
                users_with_few_tasks.append({
                    'user_id': user['id'],
                    'tasks_done': task_count
                })
        return users_with_few_tasks

    # New function to get the user's IP, state, and country
    async def get_ip(self, user_id):
        """Retrieve the user's IP address, state, and country."""
        user = await self.users_col.find_one({'id': int(user_id)})
        if user:
            return {
                'ip_address': user['ip_address'],
                'state': user['state'],
                'country': user['country']
            }
        return None

    # New function to get users statistics (total users per country and state)
    async def get_users_stats(self):
        """Get the total number of users based on country and state."""
        stats = {}
        async for user in self.users_col.find({}):
            country = user['country']
            state = user['state']
            if country not in stats:
                stats[country] = {}
            if state not in stats[country]:
                stats[country][state] = 0
            stats[country][state] += 1
        return stats


    # New Functions for Task Time Tracking
    async def task_done_time(self, user_id, domain, done_time):
        """
        Log the time a task was completed for a specific user and domain.
        """
        await self.task_time_col.insert_one({
            'user_id': int(user_id),
            'domain': domain,
            'done_time': datetime.strptime(done_time, '%Y-%m-%d %H:%M:%S')
        })

    async def time_left_24hr(self, user_id, domain):
        """
        Check how much time is left to complete 24 hours since the last task for the domain.
        """
        record = await self.task_time_col.find_one(
            {'user_id': int(user_id), 'domain': domain},
            sort=[('done_time', -1)]
        )
        if record:
            last_done_time = record['done_time']
            elapsed_time = datetime.utcnow() - last_done_time
            remaining_time = timedelta(hours=24) - elapsed_time
            if remaining_time.total_seconds() > 0:
                hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        return False

    async def is_24hr_completed(self, user_id, domain):
        """
        Check if 24 hours have passed since the last task for the user and domain.
        """
        record = await self.task_time_col.find_one(
            {'user_id': int(user_id), 'domain': domain},
            sort=[('done_time', -1)]
        )
        if record:
            last_done_time = record['done_time']
            elapsed_time = datetime.utcnow() - last_done_time
            return elapsed_time >= timedelta(hours=24)
        return True  # If no data exists, treat as 24-hour completed




db = Database(DB_URI, DB_NAME)
