export {};

declare global {
    interface Object {
        toBuffer(this: Object): Buffer;
    }
}

Object.prototype.toBuffer = function(this: Object): Buffer {
    return Buffer.from(JSON.stringify(this));
};