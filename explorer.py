#!/usr/bin/python3
from flask import Flask
from flask_restx import Api, Resource
import helpers as helpers

app = Flask(__name__)
api = Api(app, version='1.0', title='Neutrino API', description='API for USD Neutrino')

neutrino_contract_address = "3PC9BfRwJWWiw9AREE2B3eWzCks3CYtg4yo"
neutrino_account_data = helpers.get_account_data(neutrino_contract_address)
asset_ids = dict(neutrino_asset_id=helpers.filter_dict_by_key('neutrino_asset_id', neutrino_account_data),
                 bond_asset_id=helpers.filter_dict_by_key('bond_asset_id', neutrino_account_data))

contract_addresses = dict(neutrino_contract_address=neutrino_contract_address,
                          auction_contract_address=helpers.filter_dict_by_key('auction_contract',
                                                                              neutrino_account_data),
                          control_contract_address=helpers.filter_dict_by_key('control_contract',
                                                                              neutrino_account_data),
                          liquidation_contract_address=helpers.filter_dict_by_key('liquidation_contract',
                                                                                  neutrino_account_data),
                          rpd_contract_address=helpers.filter_dict_by_key('rpd_contract', neutrino_account_data))

asset_decimals = helpers.get_decimals(asset_id=asset_ids.get('neutrino_asset_id'))

WAVELET = 10 ** 8


@api.route('/price')
class Price(Resource):
    def get(self):
        return helpers.get_data_by_key(address=contract_addresses.get('control_contract_address'),
                                       key="price").get('value') / 100


@api.route('/balance')
class Balance(Resource):
    def get(self):
        return helpers.get_waves_balance(address=contract_addresses.get('neutrino_contract_address'))/WAVELET


@api.route('/total_issued')
class TotalIssued(Resource):
    def get(self):
        neutrino_balance = helpers.get_asset_balance(address=contract_addresses.get('neutrino_contract_address'),
                                                     asset_id=asset_ids.get('neutrino_asset_id')) / (
                                       10 ** asset_decimals)
        liquidation_balance = helpers.get_asset_balance(address=contract_addresses.get('liquidation_contract_address'),
                                                        asset_id=asset_ids.get('neutrino_asset_id')) / (
                                          10 ** asset_decimals)
        balance_lock_neutrino = helpers.get_data_by_key(address=contract_addresses.get('neutrino_contract_address'),
                                                        key='balance_lock_neutrino').get('value') / (
                                            10 ** asset_decimals)
        return (10 ** 12 - neutrino_balance - liquidation_balance + balance_lock_neutrino)


@api.route('/staked')
class Staked(Resource):
    def get(self):
        return helpers.get_data_by_key(address=contract_addresses.get('rpd_contract_address'),
                                       key="rpd_balance" + "_" + asset_ids.get('neutrino_asset_id')).get('value') / (
                           10 ** asset_decimals)


@api.route('/annual_yield')
class AnnualYield(Resource):
    def get(self):
        average_days = 14
        staking_address = "3P5X7AFNSTjcVoYLXkgRNTqmp51QcWAVESX"
        tx_data = helpers.get_transactions(staking_address)[0]
        filtered_tx_rewards = [obj['transfers'][0]['amount'] for obj in tx_data if obj.get('sender') ==
                            '3PLosK1gb6GpN5vV7ZyiCdwRWizpy2H31KR'][0:average_days]

        annual_yield = 365.5*(sum(filtered_tx_rewards)/average_days)/10**6
        return annual_yield


@api.route('/annual_yield_analytical')
class AnnualYieldAnalytical(Resource):
    def get(self):
        monetary_constant = 6.85
        leasing_share = 0.9
        node_performance = 0.98
        staked = Staked().get()
        total_issued = TotalIssued().get()
        staking_share = staked / total_issued
        deficit_per_cent = DeficitPerCent().get()
        deficit_coefficient = 1+(deficit_per_cent*0.01)

        return deficit_coefficient * node_performance * leasing_share * monetary_constant / staking_share


@api.route('/circulating_supply')
class CirculatingSupply(Resource):
    def get(self):
        total_issued = TotalIssued().get()
        staked = Staked().get()
        return total_issued - staked

@api.route('/deficit')
class Deficit(Resource):
    def get(self):
        total_issued = TotalIssued().get()
        balance = Balance().get()
        price = Price().get()

        balance_lock_waves = helpers.get_data_by_key(address=contract_addresses.get('neutrino_contract_address'),
                                                        key='balance_lock_waves').get('value') / (10 ** asset_decimals)

        reserve = balance - balance_lock_waves
        return (total_issued - reserve * price)


@api.route('/decimals')
class Decimals(Resource):
    def get(self):
        return asset_decimals


@api.route('/locked_for_swap')
class LockedForSwap(Resource):
    def get(self):
        return helpers.get_data_by_key(address=contract_addresses.get('neutrino_contract_address'),
                                       key='balance_lock_neutrino').get('value') / (10 ** asset_decimals)

@api.route('/deficit_per_cent')
class DeficitPerCent(Resource):
    def get(self):
        deficit = Deficit().get()
        total_issued = TotalIssued().get()
        return -1 * (deficit / total_issued) * 100


@api.route('/total_nsbt_rest')
class TotalNSBTRest(Resource):
    def get(self):
        url = 'https://beta.neutrino.at/api/v1/bonds/usd-nb_usd-n/orders'

        bonds_list = helpers.get_json(url)

        rest_amount = 0
        for i in bonds_list:
            print(i)
            rest_amount += i.get('restAmount')

        return rest_amount

@api.route('/total_nsbt_liquidation')
class TotalNSBTLiquidation(Resource):
    def get(self):
        url = 'https://beta.neutrino.at/api/v1/liquidate/usd-nb_usd-n/orders'

        bonds_list = helpers.get_json(url)

        rest_amount = 0
        for i in bonds_list:
            print(i)
            rest_amount += i.get('restTotal')

        return rest_amount


if __name__ == '__main__':
    app.run(debug=False)
