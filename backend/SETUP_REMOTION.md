# Remotion Setup (One-Time)

## Install Remotion Dependencies

Run this **ONCE** in the backend directory:

```bash
cd backend
npm install --legacy-peer-deps
```

This installs:
- `react` and `react-dom` (18.2.0)
- `remotion` and `@remotion/cli` (4.0.0)
- TypeScript and type definitions

## Why Only Once?

The old approach was installing node_modules **for every video** (wasteful and slow).

Now:
- Install Remotion **once** in `backend/node_modules`
- Each video job just creates a `Root.tsx` file
- All jobs share the same Remotion installation

## Verify Installation

Check that it worked:

```bash
ls backend/node_modules/@remotion/cli
# Should show the @remotion/cli package
```

Or test the CLI:

```bash
npx remotion --version
# Should show: 4.0.x
```

## If You Get Errors

If you see: `@remotion/cli not found in backend node_modules`

Then run:

```bash
cd backend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

## That's It!

Once installed, all Remotion video generations will use this shared installation. No more waiting for npm install on every video!
