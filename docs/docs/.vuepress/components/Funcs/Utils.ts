const deepCopy = <T>(obj: T): T => {
    const temp = JSON.stringify(obj);
    try {
        return JSON.parse(temp);
    } catch (error) {
        console.error(error);
        return {} as T;
    }
};

const isClient = typeof window !== 'undefined';

const cache = {
    set: (key: string, value: unknown) => isClient && window?.localStorage.setItem(key, JSON.stringify(value)),
    get: (key: string) => {
        if (!isClient) return null;
        const item = window?.localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    remove: (key: string) => isClient && window?.localStorage.removeItem(key),
};

export { deepCopy, cache };
