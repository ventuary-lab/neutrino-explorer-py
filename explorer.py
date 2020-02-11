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
        # asset_quantity = helpers.get_asset_quantity(asset_id=asset_ids.get('neutrino_asset_id'))
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
        monetaryConstant = 6.85
        leasingShare = 0.9
        nodePerfLagCoefficient = 0.98
        staked = Staked()
        total_issued = TotalIssued()
        stakingShare = staked.get() / total_issued.get()

        return (nodePerfLagCoefficient * leasingShare * monetaryConstant / stakingShare);


@api.route('/circulating_supply')
class CirculatingSupply(Resource):
    def get(self):
        total_issued = TotalIssued()
        staked = Staked()
        return total_issued.get() - staked.get()


@api.route('/circulating_supply_no_dec')
class CirculatingSupplyNoDec(Resource):
    def get(self):
        staked = Staked()
        total_issued = TotalIssued()
        return (total_issued.get() - staked.get()) * (10 ** asset_decimals)


@api.route('/deficit')
class Deficit(Resource):
    def get(self):
        total_issued = TotalIssued()
        balance = Balance()
        price = Price()

        balance_lock_waves = helpers.get_data_by_key(address=contract_addresses.get('neutrino_contract_address'),
                                                        key='balance_lock_waves').get('value') / (10 ** asset_decimals)

        reserve = balance.get() - balance_lock_waves
        print(total_issued.get(),reserve,price.get())

        return (total_issued.get() - reserve * price.get())


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
        deficit = Deficit()
        total_issued = TotalIssued()
        return -1 * (deficit.get() / total_issued.get()) * 100


# @api.route('/total_bonds_rest')
# class DeficitPerCent(Resource):
#     def get(self):
#         url = 'https://beta.neutrino.at/api/v1/bonds/usd-nb_usd-n/orders'
#
#         bonds_list = helpers.get_json(url)
#         print(bonds_list)
#
#         return 1
#
# @api.route('/total_bonds_liquidation')
# class DeficitPerCent(Resource):
#     def get(self):
#         url = 'https://beta.neutrino.at/api/v1/liquidate/usd-nb_usd-n/orders'
#
#         bonds_list = helpers.get_json(url)
#         print(bonds_list)
#
#         return 1


if __name__ == '__main__':
    app.run(debug=True)
