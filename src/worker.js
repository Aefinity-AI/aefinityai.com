// Serves byte ranges for /media/* (static assets alone answer Range with a full 200,
// and iOS Safari will not play video without 206). Everything else never reaches this script.
export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    const range = request.headers.get("Range");
    const ifRange = request.headers.get("If-Range");
    const plain = () => {
      const out = new Response(res.body, res);
      out.headers.set("Accept-Ranges", "bytes");
      return out;
    };
    if (!range || request.method !== "GET" || res.status !== 200 || res.headers.get("Content-Encoding")) return plain();
    if (ifRange && ifRange !== res.headers.get("ETag")) return plain();
    const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
    if (!m || (m[1] === "" && m[2] === "")) return plain();
    const buf = await res.arrayBuffer();
    const size = buf.byteLength;
    let start, end;
    if (m[1] === "") { start = Math.max(0, size - Number(m[2])); end = size - 1; }
    else { start = Number(m[1]); end = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1); }
    const headers = new Headers(res.headers);
    headers.set("Accept-Ranges", "bytes");
    if (start >= size || start > end || (m[1] === "" && Number(m[2]) === 0)) {
      headers.set("Content-Range", `bytes */${size}`);
      return new Response(null, { status: 416, headers });
    }
    headers.set("Content-Range", `bytes ${start}-${end}/${size}`);
    headers.set("Content-Length", String(end - start + 1));
    return new Response(new Uint8Array(buf, start, end - start + 1), { status: 206, headers });
  },
};
