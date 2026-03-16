interface CalcArgumentsType {
    Level: number;
    Exp: number;
    tLevel: number;
    tExp: number;
    DAILY: number;
}
interface CalcResultType {
    DAILY: number;
    total: number;
    days: number;
    target: string;
}
const leveMap = {
    1: 201,
    2: 300,
    3: 500,
    4: 700,
    5: 1000,
    6: 1500,
    7: 1600,
    8: 1700,
    9: 1900,
    10: 5500,
    11: 10000,
    12: 10000,
    13: 10000,
    14: 15000,
    15: 40000,
    16: 50000,
    17: 100000,
    18: 250000,
    19: 500000,
    20: Infinity,
};
function CalcIntimacy({ Level, Exp, tLevel, tExp, DAILY }: CalcArgumentsType): CalcResultType {
    let allExp = -Exp;
    let days = 0;
    for (let i = Level; i < tLevel; i++) {
        allExp += leveMap[i];
    }
    allExp += tExp;
    days = Math.ceil(allExp / DAILY);
    return {
        DAILY: DAILY,
        total: allExp,
        days: days,
        target: getAfterDateByDay(getCurrentDate(10), days, 10),
    };
}
function getCurrentDate(length = 19) {
    let date = new Date();
    return `${date.toLocaleDateString()}&${date.toTimeString().slice(0, 8)}`
        .replace(/(\d{4})\/(\d{1,})\/(\d{1,})&/, (all, s1, s2, s3) => {
            return `${s1}-${("0" + s2).slice(-2)}-${("0" + s3).slice(-2)} `;
        })
        .slice(0, length);
}
function getAfterDateByDay(d, n, length) {
    let drr = d.split("-");
    let date = new Date(drr[0], Number(drr[1]) - 1, Number(drr[2]) + n);
    return `${date.toLocaleDateString()}&${date.toTimeString().slice(0, 8)}`
        .replace(/(\d{4})\/(\d{1,})\/(\d{1,})&/, (all, s1, s2, s3) => {
            return `${s1}-${("0" + s2).slice(-2)}-${("0" + s3).slice(-2)} `;
        })
        .slice(0, length);
}

export { leveMap, CalcIntimacy };
