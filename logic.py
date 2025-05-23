# core.py
import numpy as np

def evaluate_project(
    land_price,
    construction_cost,
    other_cost,
    annual_rent,
    vacancy_rate,
    opex_rate,
    years=20,
):
    """基本的な収益シミュレーション & IRR 計算"""
    # 毎年のキャッシュフロー
    gross_rent = annual_rent * (1 - vacancy_rate)
    opex = gross_rent * opex_rate
    noi = gross_rent - opex
    cash_flows = [- (land_price + construction_cost + other_cost)]  # 年0
    cash_flows += [noi] * years                                    # 年1〜n
    cash_flows[-1] += land_price * 0.9  # 最終年に90%で売却すると仮定

    irr = np.irr(cash_flows) * 100
    npv = np.npv(0.06, cash_flows)  # 割引率6%例
    return {"IRR(%)": round(irr, 2), "NPV": round(npv, 0), "NOI/年": round(noi, 0)}
