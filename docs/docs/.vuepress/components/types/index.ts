export interface ICol {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
}

export type TOptionStyle = "input" | "check";

export type TInputType = "number" | "text";

export interface IOption {
    prop: string;
    name: string;
    style: TOptionStyle;
    type?: TInputType;
    info?: string;
    required?: boolean;
}

export interface IConfig {
    col: ICol;
    items: IOption[];
}
