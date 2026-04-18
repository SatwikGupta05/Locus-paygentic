import { NextResponse } from "next/server";
import { readContractState } from "@/lib/contract/erc8004Reader";

export const revalidate = 30;

export async function GET() {
  try {
    const state = await readContractState();
    return NextResponse.json(state);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Contract read failed"
      },
      { status: 500 }
    );
  }
}
