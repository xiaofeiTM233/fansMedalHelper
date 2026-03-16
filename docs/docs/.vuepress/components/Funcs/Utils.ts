const deepCopy = (obj) => {
    const temp = JSON.stringify(obj);
    try {
        return JSON.parse(temp);
    } catch (error) {
        console.error(error);
        return {};
    }
};

const cache = {
    set: (key: string, value: any) => window?.localStorage.setItem(key, JSON.stringify(value)),
    get: (key: string) =>
        // ignore error here plz.
        window?.localStorage.getItem(key) ? JSON.parse(window?.localStorage.getItem(key)) : null,
    remove: (key: string) => window?.localStorage.removeItem(key),
};

export { deepCopy, cache };
