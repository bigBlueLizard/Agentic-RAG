import { Chat } from "@/components/chat/Chat";
import Navbar from "@/components/navbar";
import OpenAPIEditor from "@/components/openapi/editor";

export default function Dashboard() {
    return <>
        {/* <Navbar /> */}
        <div className="flex w-full">
            <div className="w-full pt-2 pl-2 max-h-screen overflow-y-scroll">
                <OpenAPIEditor />
                
            </div>
            <div className="w-full pt-2 pr-2">
                <Chat />
            </div>
        </div>
    </>
}